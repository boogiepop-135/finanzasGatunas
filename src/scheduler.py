"""
Scheduler de tareas automáticas para Finanzas Gatunas.
Envía recordatorios y resúmenes vía Telegram usando APScheduler.
"""
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Zona horaria de México (Centro)
TIMEZONE = pytz.timezone(os.environ.get("TIMEZONE", "America/Mexico_City"))


def _get_context(db, usuario_id: str) -> dict:
    """Construir el contexto financiero de un usuario para el scheduler."""
    from datetime import datetime, timedelta

    hoy = datetime.now()
    inicio_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
    fin_mes = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    fin_mes_str = fin_mes.strftime("%Y-%m-%d")

    # Ingresos del mes
    ing_cur = db.transacciones.aggregate([
        {"$match": {"usuario_id": usuario_id, "tipo": "ingreso",
                    "fecha": {"$gte": inicio_mes, "$lte": fin_mes_str}}},
        {"$group": {"_id": None, "total": {"$sum": "$monto"}}}
    ])
    ingresos_mes = next(ing_cur, {}).get("total", 0) or 0

    # Gastos del mes
    gas_cur = db.transacciones.aggregate([
        {"$match": {"usuario_id": usuario_id, "tipo": "gasto",
                    "fecha": {"$gte": inicio_mes, "$lte": fin_mes_str}}},
        {"$group": {"_id": None, "total": {"$sum": "$monto"}}}
    ])
    gastos_mes = next(gas_cur, {}).get("total", 0) or 0

    # Membresías activas
    mem_cur = db.membresias.aggregate([
        {"$match": {"usuario_id": usuario_id, "estado": "activa"}},
        {"$group": {"_id": None, "total": {"$sum": "$monto_mensual"}}}
    ])
    membresias = next(mem_cur, {}).get("total", 0) or 0

    # Balance total histórico
    total_ing_cur = db.transacciones.aggregate([
        {"$match": {"usuario_id": usuario_id, "tipo": "ingreso"}},
        {"$group": {"_id": None, "total": {"$sum": "$monto"}}}
    ])
    total_gas_cur = db.transacciones.aggregate([
        {"$match": {"usuario_id": usuario_id, "tipo": "gasto"}},
        {"$group": {"_id": None, "total": {"$sum": "$monto"}}}
    ])
    total_ing = next(total_ing_cur, {}).get("total", 0) or 0
    total_gas = next(total_gas_cur, {}).get("total", 0) or 0

    # Top categorías del mes
    top_cur = db.transacciones.aggregate([
        {"$match": {"usuario_id": usuario_id, "tipo": "gasto",
                    "fecha": {"$gte": inicio_mes, "$lte": fin_mes_str}}},
        {"$group": {"_id": "$categoria_id", "total": {"$sum": "$monto"}}},
        {"$sort": {"total": -1}},
        {"$limit": 5}
    ])
    top_categorias = []
    for item in top_cur:
        if item.get("_id"):
            from bson import ObjectId
            cat = db.categorias.find_one({"_id": ObjectId(item["_id"])})
            if cat:
                top_categorias.append({"nombre": cat.get("nombre"), "total": item.get("total", 0)})

    # Recordatorios pendientes
    pendientes = db.recordatorios.count_documents({"usuario_id": usuario_id, "estado": "pendiente"})

    return {
        "balance": total_ing - total_gas,
        "ingresos_mes": ingresos_mes,
        "gastos_mes": gastos_mes,
        "membresias_mensual": membresias,
        "membresias": membresias,
        "top_categorias": top_categorias,
        "recordatorios_pendientes": pendientes,
        "mes_actual": hoy.strftime("%B %Y"),
    }


def job_recordatorios_diarios(db):
    """
    Job diario: avisa a los usuarios sobre pagos próximos (<=3 días).
    Se ejecuta todos los días a las 9:00 AM (hora México).
    """
    if db is None:
        return

    print(f"[SCHEDULER] Ejecutando recordatorios diarios — {datetime.now()}")
    hoy = datetime.now()
    fecha_limite = (hoy + timedelta(days=3)).strftime("%Y-%m-%d")
    fecha_hoy = hoy.strftime("%Y-%m-%d")

    try:
        recordatorios = list(db.recordatorios.find({
            "estado": "pendiente",
            "fecha_vencimiento": {"$gte": fecha_hoy, "$lte": fecha_limite}
        }))

        procesados = 0
        for rec in recordatorios:
            usuario_id = rec.get("usuario_id")
            if not usuario_id:
                continue

            usuario = db.usuarios.find_one({"_id": __import__("bson").ObjectId(usuario_id)}) if len(usuario_id) == 24 else db.usuarios.find_one({"_id": usuario_id})
            if not usuario:
                continue

            chat_id = usuario.get("telegram_chat_id")
            if not chat_id:
                continue  # Usuario sin Telegram vinculado

            from telegram_bot import send_reminder
            if send_reminder(chat_id, {
                "nombre": rec.get("nombre", "Pago"),
                "monto": rec.get("monto", 0),
                "fecha_vencimiento": rec.get("fecha_vencimiento"),
            }):
                procesados += 1

        print(f"[SCHEDULER] Recordatorios enviados: {procesados}/{len(recordatorios)}")

    except Exception as e:
        print(f"[ERROR] Error en job_recordatorios_diarios: {e}")


def job_recordatorios_membresias(db):
    """
    Job diario: avisa cuando hay membresías próximas a renovarse (<=3 días).
    """
    if db is None:
        return

    print(f"[SCHEDULER] Ejecutando recordatorios de membresías — {datetime.now()}")
    hoy = datetime.now()
    fecha_limite = (hoy + timedelta(days=3)).strftime("%Y-%m-%d")
    fecha_hoy = hoy.strftime("%Y-%m-%d")

    try:
        membresias = list(db.membresias.find({
            "estado": "activa",
            "fecha_renovacion": {"$gte": fecha_hoy, "$lte": fecha_limite}
        }))

        for mem in membresias:
            usuario_id = mem.get("usuario_id")
            if not usuario_id:
                continue

            try:
                from bson import ObjectId
                usuario = db.usuarios.find_one({"_id": ObjectId(usuario_id)})
            except Exception:
                continue

            if not usuario:
                continue

            chat_id = usuario.get("telegram_chat_id")
            if not chat_id:
                continue

            fecha_renovacion = mem.get("fecha_renovacion", "")
            try:
                fecha_dt = datetime.strptime(fecha_renovacion, "%Y-%m-%d")
                dias_restantes = (fecha_dt - hoy).days
            except Exception:
                dias_restantes = 1

            from telegram_bot import send_membership_reminder
            send_membership_reminder(chat_id, {
                "nombre": mem.get("nombre", "Suscripción"),
                "monto_mensual": mem.get("monto_mensual", 0),
                "fecha_renovacion": fecha_renovacion,
            }, max(0, dias_restantes))

    except Exception as e:
        print(f"[ERROR] Error en job_recordatorios_membresias: {e}")


def job_resumen_mensual(db):
    """
    Job mensual: el día 1 de cada mes a las 9am, envía un resumen del mes anterior.
    """
    if db is None:
        return

    print(f"[SCHEDULER] Ejecutando resumen mensual — {datetime.now()}")

    try:
        usuarios = list(db.usuarios.find({"telegram_chat_id": {"$exists": True, "$ne": ""}}))
        print(f"[SCHEDULER] Usuarios con Telegram: {len(usuarios)}")

        for usuario in usuarios:
            chat_id = usuario.get("telegram_chat_id")
            if not chat_id:
                continue

            usuario_id = str(usuario["_id"])
            context = _get_context(db, usuario_id)

            # Intentar agregar análisis de IA
            ai_text = None
            try:
                from ai_advisor import analyze_monthly_spending
                ai_text = analyze_monthly_spending(context)
            except Exception:
                pass

            from telegram_bot import send_weekly_summary
            send_weekly_summary(chat_id, {
                "ingresos": context["ingresos_mes"],
                "gastos": context["gastos_mes"],
                "balance": context["balance"],
                "membresias": context["membresias"],
                "recordatorios_pendientes": context["recordatorios_pendientes"],
            }, ai_text)

    except Exception as e:
        print(f"[ERROR] Error en job_resumen_mensual: {e}")


def job_alerta_presupuestos(db):
    """
    Job semanal: detecta categorías donde el usuario superó el 80% de su presupuesto mensual.
    """
    if db is None:
        return

    print(f"[SCHEDULER] Verificando alertas de presupuesto — {datetime.now()}")
    hoy = datetime.now()
    inicio_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
    fin_mes_str = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    fin_mes_str = fin_mes_str.strftime("%Y-%m-%d")
    mes = hoy.month
    año = hoy.year

    try:
        usuarios = list(db.usuarios.find({"telegram_chat_id": {"$exists": True, "$ne": ""}}))

        for usuario in usuarios:
            chat_id = usuario.get("telegram_chat_id")
            usuario_id = str(usuario["_id"])

            presupuestos = list(db.presupuestos.find({
                "usuario_id": usuario_id,
                "mes": mes,
                "año": año,
                "monto": {"$gt": 0}
            }))

            for pres in presupuestos:
                categoria_id = pres.get("categoria_id")
                presupuesto_monto = pres.get("monto", 0)
                if presupuesto_monto <= 0 or not categoria_id:
                    continue

                # Sumar gastos de esa categoría este mes
                cur = db.transacciones.aggregate([
                    {"$match": {
                        "usuario_id": usuario_id,
                        "categoria_id": categoria_id,
                        "tipo": "gasto",
                        "fecha": {"$gte": inicio_mes, "$lte": fin_mes_str}
                    }},
                    {"$group": {"_id": None, "total": {"$sum": "$monto"}}}
                ])
                gastado = next(cur, {}).get("total", 0) or 0

                porcentaje = gastado / presupuesto_monto * 100
                if porcentaje >= 80:
                    from bson import ObjectId
                    cat = db.categorias.find_one({"_id": ObjectId(categoria_id)})
                    if cat:
                        from telegram_bot import send_budget_alert
                        send_budget_alert(chat_id, cat.get("nombre", "Categoría"), gastado, presupuesto_monto)

    except Exception as e:
        print(f"[ERROR] Error en job_alerta_presupuestos: {e}")


def create_scheduler(db):
    """
    Crear y configurar el scheduler con todos los jobs.
    
    Args:
        db: Instancia de MongoDB
    
    Returns:
        BackgroundScheduler configurado (sin iniciar)
    """
    scheduler = BackgroundScheduler(timezone=TIMEZONE)

    # Recordatorios de pagos: diario a las 9:00 AM
    scheduler.add_job(
        func=job_recordatorios_diarios,
        trigger=CronTrigger(hour=9, minute=0, timezone=TIMEZONE),
        args=[db],
        id="recordatorios_diarios",
        name="Recordatorios diarios de pagos",
        replace_existing=True,
    )

    # Recordatorios de membresías: diario a las 9:05 AM
    scheduler.add_job(
        func=job_recordatorios_membresias,
        trigger=CronTrigger(hour=9, minute=5, timezone=TIMEZONE),
        args=[db],
        id="recordatorios_membresias",
        name="Recordatorios de membresías próximas",
        replace_existing=True,
    )

    # Resumen mensual: día 1 de cada mes a las 9:00 AM
    scheduler.add_job(
        func=job_resumen_mensual,
        trigger=CronTrigger(day=1, hour=9, minute=0, timezone=TIMEZONE),
        args=[db],
        id="resumen_mensual",
        name="Resumen mensual de finanzas",
        replace_existing=True,
    )

    # Alertas de presupuesto: lunes a las 10:00 AM
    scheduler.add_job(
        func=job_alerta_presupuestos,
        trigger=CronTrigger(day_of_week="mon", hour=10, minute=0, timezone=TIMEZONE),
        args=[db],
        id="alerta_presupuestos",
        name="Alertas de presupuesto mensual",
        replace_existing=True,
    )

    return scheduler
