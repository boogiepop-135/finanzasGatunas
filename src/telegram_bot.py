"""
Módulo del Bot de Telegram para Finanzas Gatunas
Maneja el envío de notificaciones, recordatorios y el proceso de vinculación de cuentas.
"""
import os
import requests
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def _post(endpoint: str, payload: dict) -> dict | None:
    """Helper interno para hacer POST a la API de Telegram."""
    if not TELEGRAM_TOKEN:
        print("[WARNING] TELEGRAM_BOT_TOKEN no configurado. Telegram desactivado.")
        return None
    try:
        url = f"{BASE_URL}/{endpoint}"
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[ERROR] Error comunicando con Telegram: {e}")
        return None


def send_message(chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
    """Enviar un mensaje de texto a un chat de Telegram."""
    result = _post("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    })
    if result and result.get("ok"):
        return True
    print(f"[ERROR] Fallo al enviar mensaje Telegram: {result}")
    return False


def set_webhook(webhook_url: str) -> bool:
    """Configurar el webhook para recibir actualizaciones del bot."""
    result = _post("setWebhook", {"url": webhook_url})
    if result and result.get("ok"):
        print(f"[OK] Webhook de Telegram configurado: {webhook_url}")
        return True
    print(f"[ERROR] Fallo al configurar webhook: {result}")
    return False


def delete_webhook() -> bool:
    """Eliminar el webhook (útil para desarrollo/polling)."""
    result = _post("deleteWebhook", {})
    return bool(result and result.get("ok"))


# =====================================================
# Mensajes prediseñados
# =====================================================

def send_reminder(chat_id: str, recordatorio: dict) -> bool:
    """
    Enviar recordatorio de pago próximo.
    
    Args:
        chat_id: ID del chat de Telegram del usuario
        recordatorio: Dict con nombre, monto, fecha_vencimiento
    """
    nombre = recordatorio.get("nombre", "Pago")
    monto = recordatorio.get("monto", 0)
    fecha = recordatorio.get("fecha_vencimiento", "pronto")

    text = (
        f"🔔 <b>Recordatorio de pago</b>\n\n"
        f"📋 <b>{nombre}</b>\n"
        f"💰 ${monto:.2f}\n"
        f"📅 Vence: {fecha}\n\n"
        f"Abre Finanzas Gatunas para marcarlo como pagado."
    )
    return send_message(chat_id, text)


def send_membership_reminder(chat_id: str, membresia: dict, dias_restantes: int) -> bool:
    """
    Enviar recordatorio de renovación de membresía.
    
    Args:
        chat_id: ID del chat de Telegram
        membresia: Dict con nombre, monto_mensual, fecha_renovacion
        dias_restantes: Días que faltan para la renovación
    """
    nombre = membresia.get("nombre", "Suscripción")
    monto = membresia.get("monto_mensual", 0)
    fecha = membresia.get("fecha_renovacion", "")

    if dias_restantes == 0:
        urgencia = "¡<b>HOY</b> se renueva"
        emoji = "⚡"
    elif dias_restantes == 1:
        urgencia = "se renueva <b>mañana</b>"
        emoji = "⏰"
    else:
        urgencia = f"se renueva en <b>{dias_restantes} días</b>"
        emoji = "🗓️"

    text = (
        f"{emoji} <b>Renovación próxima</b>\n\n"
        f"📺 <b>{nombre}</b> {urgencia}\n"
        f"💰 Se cargará: ${monto:.2f}\n"
        f"📅 Fecha: {fecha}"
    )
    return send_message(chat_id, text)


def send_weekly_summary(chat_id: str, resumen: dict, ai_analysis: str = None) -> bool:
    """
    Enviar resumen semanal/mensual de finanzas.
    
    Args:
        chat_id: ID del chat de Telegram
        resumen: Dict con ingresos, gastos, balance, top_categoria
        ai_analysis: Análisis generado por Gemini IA (opcional)
    """
    ingresos = resumen.get("ingresos", 0)
    gastos = resumen.get("gastos", 0)
    balance = resumen.get("balance", 0)
    membresias = resumen.get("membresias", 0)
    recordatorios_pendientes = resumen.get("recordatorios_pendientes", 0)

    balance_emoji = "📈" if balance >= 0 else "📉"
    balance_str = f"+${balance:.2f}" if balance >= 0 else f"-${abs(balance):.2f}"

    # Recordatorio de pagos pendientes
    recordatorio_str = ""
    if recordatorios_pendientes > 0:
        recordatorio_str = f"\n⚠️ Tienes <b>{recordatorios_pendientes}</b> pago(s) pendiente(s)"

    text = (
        f"🐱 <b>Tu resumen mensual — Finanzas Gatunas</b>\n\n"
        f"💰 Ingresos: ${ingresos:.2f}\n"
        f"💸 Gastos: ${gastos:.2f}\n"
        f"🔄 Membresías: ${membresias:.2f}/mes\n"
        f"{balance_emoji} Balance: <b>{balance_str}</b>"
        f"{recordatorio_str}"
    )

    if ai_analysis:
        text += f"\n\n🤖 <i>{ai_analysis}</i>"

    return send_message(chat_id, text)


def send_budget_alert(chat_id: str, categoria: str, gastado: float, presupuesto: float) -> bool:
    """
    Enviar alerta cuando el usuario supera el 80% de su presupuesto en una categoría.
    
    Args:
        chat_id: ID del chat de Telegram
        categoria: Nombre de la categoría
        gastado: Monto gastado en la categoría este mes
        presupuesto: Presupuesto mensual asignado
    """
    porcentaje = (gastado / presupuesto * 100) if presupuesto > 0 else 0
    restante = presupuesto - gastado

    if porcentaje >= 100:
        titulo = "🚨 ¡Presupuesto superado!"
        detalle = f"Ya gastaste ${abs(restante):.2f} de más"
    else:
        titulo = "⚠️ Presupuesto al límite"
        detalle = f"Solo te quedan ${restante:.2f}"

    text = (
        f"{titulo}\n\n"
        f"📂 Categoría: <b>{categoria}</b>\n"
        f"💸 Gastado: ${gastado:.2f} de ${presupuesto:.2f} ({porcentaje:.0f}%)\n"
        f"{detalle}"
    )
    return send_message(chat_id, text)


def send_link_success(chat_id: str, nombre_usuario: str) -> bool:
    """Confirmar al usuario que su cuenta de Telegram fue vinculada correctamente."""
    text = (
        f"🐱 ¡Hola, <b>{nombre_usuario}</b>!\n\n"
        f"Tu cuenta de Telegram quedó vinculada con Finanzas Gatunas.\n\n"
        f"Desde ahora recibirás:\n"
        f"🔔 Recordatorios de pagos próximos\n"
        f"📊 Resumen mensual de tus finanzas\n"
        f"⚠️ Alertas de presupuesto\n\n"
        f"¡Que tus finanzas siempre estén en verde! 💰"
    )
    return send_message(chat_id, text)


def send_link_instructions(chat_id: str) -> bool:
    """Enviar instrucciones de uso al nuevo usuario vinculado."""
    text = (
        f"📋 <b>Comandos disponibles</b>\n\n"
        f"Actualmente el bot funciona en modo notificaciones automáticas.\n"
        f"Para gestionar tus finanzas, visita la app web.\n\n"
        f"Recibirás notificaciones automáticamente según tu configuración."
    )
    return send_message(chat_id, text)


# =====================================================
# Procesamiento de mensajes entrantes (webhook)
# =====================================================

def process_update(update: dict, db) -> None:
    """
    Procesar una actualización entrante del bot de Telegram.
    Maneja el comando /start para vincular cuentas.
    
    Args:
        update: Dict con la actualización de Telegram
        db: Instancia de la base de datos MongoDB
    """
    message = update.get("message", {})
    if not message:
        return

    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "").strip()
    from_user = message.get("from", {})
    telegram_nombre = from_user.get("first_name", "Usuario")

    if not chat_id or not text:
        return

    # Comando /start con código de vinculación
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1:
            # Tiene código de vinculación
            codigo = parts[1].strip()
            _vincular_cuenta(chat_id, codigo, telegram_nombre, db)
        else:
            # /start sin código
            msg = (
                f"🐱 ¡Hola, {telegram_nombre}!\n\n"
                f"Soy el bot de <b>Finanzas Gatunas</b>.\n\n"
                f"Para vincular tu cuenta, ve a la app web y haz clic en "
                f"<b>Conectar Telegram</b> en tu perfil. "
                f"Te daré un código que debes enviarme aquí."
            )
            send_message(chat_id, msg)

    elif text == "/desconectar":
        _desconectar_cuenta(chat_id, db)

    elif text.startswith('/balance'):
        _cmd_balance(chat_id, db)

    elif text.startswith('/gastos'):
        _cmd_gastos(chat_id, db)

    elif text.startswith('/mes'):
        _cmd_mes(chat_id, db)

    elif text.startswith('/gasto '):
        # /gasto Almuerzo 120
        partes = text[7:].strip().rsplit(' ', 1)
        if len(partes) == 2:
            descripcion, monto_str = partes
            try:
                monto = float(monto_str.replace(',', '.'))
                _cmd_gasto_rapido(chat_id, db, descripcion.strip(), monto)
            except ValueError:
                send_message(chat_id, "❌ Formato inválido. Usa: /gasto Descripción 120.50")
        else:
            send_message(chat_id, "❌ Uso: /gasto <descripción> <monto>\nEjemplo: /gasto Almuerzo 120")

    elif text.startswith('/ayuda') or text.startswith('/help'):
        send_message(
            chat_id,
            "🐱 <b>Comandos de Finanzas Gatunas</b>\n\n"
            "/balance — Ver tu balance actual\n"
            "/gastos — Ver gastos por categoría este mes\n"
            "/mes — Resumen financiero del mes\n"
            "/gasto &lt;desc&gt; &lt;monto&gt; — Registrar gasto rápido\n"
            "/desconectar — Desvincular cuenta Telegram\n"
            "/start &lt;código&gt; — Vincular cuenta\n\n"
            "📱 Para más funciones visita la app web."
        )

    else:
        # Mensaje no reconocido
        send_message(
            chat_id,
            "🐱 No entendí ese mensaje. Escribe /ayuda para ver los comandos disponibles."
        )


def _vincular_cuenta(chat_id: str, codigo: str, telegram_nombre: str, db) -> None:
    """Vincular el chat_id de Telegram con el usuario que tiene ese código."""
    if db is None:
        send_message(chat_id, "😿 Error de conexión. Intenta más tarde.")
        return

    try:
        from datetime import datetime
        # Buscar usuario con ese código pendiente
        usuario = db.usuarios.find_one({
            "telegram_link_code": codigo,
            "telegram_link_code_expires": {"$gt": datetime.now()}
        })

        if not usuario:
            send_message(
                chat_id,
                "❌ Código inválido o expirado.\n\n"
                "Genera un nuevo código desde la app web en <b>Configuración → Conectar Telegram</b>."
            )
            return

        # Actualizar el usuario con el chat_id de Telegram
        db.usuarios.update_one(
            {"_id": usuario["_id"]},
            {
                "$set": {
                    "telegram_chat_id": chat_id,
                    "telegram_nombre": telegram_nombre,
                    "telegram_vinculado_at": datetime.now(),
                },
                "$unset": {
                    "telegram_link_code": "",
                    "telegram_link_code_expires": ""
                }
            }
        )

        nombre_usuario = usuario.get("nombre") or telegram_nombre
        send_link_success(chat_id, nombre_usuario)
        send_link_instructions(chat_id)
        print(f"[OK] Cuenta Telegram vinculada: chat_id={chat_id}, usuario={usuario.get('email')}")

    except Exception as e:
        print(f"[ERROR] Error vinculando cuenta Telegram: {e}")
        send_message(chat_id, "😿 Ocurrió un error al vincular tu cuenta. Intenta de nuevo.")


def _desconectar_cuenta(chat_id: str, db) -> None:
    """Desconectar la cuenta de Telegram."""
    if db is None:
        return
    try:
        result = db.usuarios.update_one(
            {"telegram_chat_id": chat_id},
            {"$unset": {"telegram_chat_id": "", "telegram_nombre": "", "telegram_vinculado_at": ""}}
        )
        if result.modified_count > 0:
            send_message(chat_id, "✅ Tu cuenta de Telegram fue desvinculada de Finanzas Gatunas.")
        else:
            send_message(chat_id, "ℹ️ No encontré ninguna cuenta vinculada a este chat.")
    except Exception as e:
        print(f"[ERROR] Error desconectando cuenta Telegram: {e}")


# ===== COMANDOS INTERACTIVOS =====

def _get_usuario_by_chat(chat_id: str, db):
    """Obtener usuario vinculado a un chat_id."""
    if db is None:
        return None
    return db.usuarios.find_one({"telegram_chat_id": chat_id})


def _cmd_balance(chat_id: str, db) -> None:
    """Responder con el balance actual del usuario."""
    usuario = _get_usuario_by_chat(chat_id, db)
    if not usuario:
        send_message(chat_id, "⚠️ Necesitas vincular tu cuenta primero. Usa /start <código>.")
        return
    try:
        from datetime import datetime, timedelta
        usuario_id = str(usuario["_id"])
        cur = db.transacciones.aggregate([
            {"$match": {"usuario_id": usuario_id}},
            {"$group": {
                "_id": "$tipo",
                "total": {"$sum": "$monto"}
            }}
        ])
        totales = {r["_id"]: r["total"] for r in cur}
        ingresos = totales.get("ingreso", 0)
        gastos = totales.get("gasto", 0)
        balance = ingresos - gastos
        emoji = "✅" if balance >= 0 else "🔴"
        send_message(
            chat_id,
            f"💰 <b>Tu Balance</b>\n\n"
            f"📈 Ingresos totales: <b>${ingresos:,.2f}</b>\n"
            f"📉 Gastos totales: <b>${gastos:,.2f}</b>\n"
            f"{emoji} Balance: <b>${balance:,.2f}</b>"
        )
    except Exception as e:
        print(f"[ERROR] _cmd_balance: {e}")
        send_message(chat_id, "😿 Ocurrió un error al obtener tu balance.")


def _cmd_gastos(chat_id: str, db) -> None:
    """Responder con los gastos por categoría del mes actual."""
    usuario = _get_usuario_by_chat(chat_id, db)
    if not usuario:
        send_message(chat_id, "⚠️ Necesitas vincular tu cuenta primero.")
        return
    try:
        from datetime import datetime, timedelta
        from bson import ObjectId
        usuario_id = str(usuario["_id"])
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
        fin_mes = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        cur = db.transacciones.aggregate([
            {"$match": {"usuario_id": usuario_id, "tipo": "gasto",
                        "fecha": {"$gte": inicio_mes, "$lte": fin_mes.strftime("%Y-%m-%d")}}},
            {"$group": {"_id": "$categoria_id", "total": {"$sum": "$monto"}}},
            {"$sort": {"total": -1}},
            {"$limit": 7}
        ])
        filas = list(cur)
        if not filas:
            send_message(chat_id, "📊 No tienes gastos registrados este mes.")
            return
        lineas = [f"📊 <b>Gastos de {hoy.strftime('%B %Y')}</b>\n"]
        for item in filas:
            cat_id = item.get("_id", "")
            nombre = "Sin categoría"
            if cat_id:
                cat = db.categorias.find_one({"_id": ObjectId(cat_id)})
                if cat:
                    nombre = cat.get("nombre", nombre)
            lineas.append(f"• {nombre}: <b>${item['total']:,.2f}</b>")
        send_message(chat_id, "\n".join(lineas))
    except Exception as e:
        print(f"[ERROR] _cmd_gastos: {e}")
        send_message(chat_id, "😿 Ocurrió un error al obtener tus gastos.")


def _cmd_mes(chat_id: str, db) -> None:
    """Resumen financiero del mes actual."""
    usuario = _get_usuario_by_chat(chat_id, db)
    if not usuario:
        send_message(chat_id, "⚠️ Necesitas vincular tu cuenta primero.")
        return
    try:
        from datetime import datetime, timedelta
        usuario_id = str(usuario["_id"])
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
        fin_mes = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        fin_mes_str = fin_mes.strftime("%Y-%m-%d")
        cur = db.transacciones.aggregate([
            {"$match": {"usuario_id": usuario_id,
                        "fecha": {"$gte": inicio_mes, "$lte": fin_mes_str}}},
            {"$group": {"_id": "$tipo", "total": {"$sum": "$monto"}}}
        ])
        totales = {r["_id"]: r["total"] for r in cur}
        ingresos = totales.get("ingreso", 0)
        gastos = totales.get("gasto", 0)
        balance = ingresos - gastos
        emoji = "✅" if balance >= 0 else "⚠️"
        send_message(
            chat_id,
            f"📅 <b>Resumen de {hoy.strftime('%B %Y')}</b>\n\n"
            f"📈 Ingresos: <b>${ingresos:,.2f}</b>\n"
            f"📉 Gastos: <b>${gastos:,.2f}</b>\n"
            f"{emoji} Saldo del mes: <b>${balance:,.2f}</b>"
        )
    except Exception as e:
        print(f"[ERROR] _cmd_mes: {e}")
        send_message(chat_id, "😿 Ocurrió un error al obtener el resumen.")


def _cmd_gasto_rapido(chat_id: str, db, descripcion: str, monto: float) -> None:
    """Registrar un gasto rápido desde Telegram."""
    usuario = _get_usuario_by_chat(chat_id, db)
    if not usuario:
        send_message(chat_id, "⚠️ Necesitas vincular tu cuenta primero.")
        return
    if monto <= 0:
        send_message(chat_id, "❌ El monto debe ser mayor a 0.")
        return
    try:
        from datetime import datetime
        usuario_id = str(usuario["_id"])
        hoy = datetime.now().strftime("%Y-%m-%d")
        db.transacciones.insert_one({
            "usuario_id": usuario_id,
            "descripcion": descripcion,
            "monto": monto,
            "tipo": "gasto",
            "fecha": hoy,
            "categoria_id": "",
            "tarjeta_id": "",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "source": "telegram"
        })
        send_message(
            chat_id,
            f"✅ Gasto registrado:\n"
            f"📝 {descripcion}\n"
            f"💸 <b>${monto:,.2f}</b>\n"
            f"📅 {hoy}"
        )
    except Exception as e:
        print(f"[ERROR] _cmd_gasto_rapido: {e}")
        send_message(chat_id, "😿 Ocurrió un error al registrar el gasto.")
