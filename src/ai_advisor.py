"""
Módulo de asesor financiero con IA usando Gemini API
"""
import os
import google.generativeai as genai
from datetime import datetime

# Configurar Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Eres "Gatito Financiero" 🐱, un asesor financiero personal amigable e inteligente integrado en Finanzas Gatunas, una app de gestión de finanzas del hogar.

Tu personalidad:
- Amigable, cálido y empático, como un gato inteligente que cuida a su dueño
- Usa emojis de vez en cuando (especialmente 🐱, 💰, 📊) para mantener el tono
- Respuestas concisas: máximo 3-4 párrafos cortos
- Siempre en español

Tus capacidades:
- Analizar los datos financieros reales del usuario que te proporcionan
- Dar consejos concretos basados en esos datos
- Detectar patrones de gasto y tendencias
- Sugerir cómo mejorar el balance mensual

Reglas importantes:
- NUNCA inventes datos o cifras que no estén en el contexto del usuario
- Si no tienes suficiente información, dilo y sugiere qué hacer
- Enfócate en observaciones útiles y accionables
- Si el balance es negativo, ayuda con gentileza, no con alarma"""


def get_ai_advice(user_message: str, financial_context: dict) -> str:
    """
    Obtener consejo de Gemini basado en la pregunta del usuario y su contexto financiero.
    
    Args:
        user_message: Pregunta o mensaje del usuario
        financial_context: Diccionario con datos financieros del usuario
    
    Returns:
        Respuesta de texto del asesor IA
    """
    if not GEMINI_API_KEY:
        return "⚠️ El asesor IA no está configurado. Agrega tu GEMINI_API_KEY al archivo .env para activarlo."

    try:
        # Construir el contexto financiero para el modelo
        balance = financial_context.get("balance", 0)
        ingresos_mes = financial_context.get("ingresos_mes", 0)
        gastos_mes = financial_context.get("gastos_mes", 0)
        membresias_mensual = financial_context.get("membresias_mensual", 0)
        top_categorias = financial_context.get("top_categorias", [])
        recordatorios_pendientes = financial_context.get("recordatorios_pendientes", 0)
        mes_actual = financial_context.get("mes_actual", datetime.now().strftime("%B %Y"))

        # Formatear categorías
        categorias_str = ""
        if top_categorias:
            categorias_str = "\n".join(
                [f"  - {c['nombre']}: ${c['total']:.2f}" for c in top_categorias[:5]]
            )
        else:
            categorias_str = "  Sin datos de categorías aún"

        # Determinar estado del balance
        estado_balance = "positivo ✅" if balance >= 0 else "negativo ⚠️"

        context_prompt = f"""
=== DATOS FINANCIEROS DEL USUARIO ({mes_actual}) ===
Balance total: ${balance:.2f} ({estado_balance})
Ingresos del mes actual: ${ingresos_mes:.2f}
Gastos del mes actual: ${gastos_mes:.2f}
Membresías/suscripciones mensuales: ${membresias_mensual:.2f}/mes
Recordatorios de pagos pendientes: {recordatorios_pendientes}

Top categorías de gasto este mes:
{categorias_str}
==========================================

Pregunta del usuario: {user_message}
"""

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\n{context_prompt}",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=500,
                temperature=0.7,
            ),
        )

        return response.text

    except Exception as e:
        print(f"[ERROR] Error con Gemini API: {e}")
        return f"😿 Tuve un problema al procesar tu pregunta. Por favor intenta de nuevo en un momento."


def analyze_monthly_spending(financial_context: dict) -> str:
    """
    Generar un análisis automático mensual de los gastos del usuario.
    Útil para el resumen que envía el bot de Telegram.
    """
    if not GEMINI_API_KEY:
        return None

    try:
        balance = financial_context.get("balance", 0)
        ingresos_mes = financial_context.get("ingresos_mes", 0)
        gastos_mes = financial_context.get("gastos_mes", 0)
        top_categorias = financial_context.get("top_categorias", [])

        categorias_str = ""
        if top_categorias:
            categorias_str = ", ".join(
                [f"{c['nombre']} (${c['total']:.2f})" for c in top_categorias[:3]]
            )

        prompt = f"""
{SYSTEM_PROMPT}

Genera un análisis financiero mensual muy breve (máximo 3 oraciones) para Telegram.
Formato: mensaje directo, sin markdown complejo, solo emojis y texto plano.

Datos del mes:
- Ingresos: ${ingresos_mes:.2f}
- Gastos: ${gastos_mes:.2f}  
- Balance: ${balance:.2f}
- Top gastos: {categorias_str}

Sé conciso. El usuario recibirá esto en Telegram.
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=200,
                temperature=0.5,
            ),
        )
        return response.text

    except Exception as e:
        print(f"[ERROR] Error generando análisis mensual: {e}")
        return None
