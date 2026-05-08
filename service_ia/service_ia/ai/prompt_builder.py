import json

from .task_router import obtener_modo_respuesta


PROMPT_BASE_RECOMENDADOR = """
Eres una IA educativa dentro de Alejandrias Library.

TAREA:
Recomendar foros relevantes.
""".strip()


PROMPT_BASE_CHAT = """
Eres AlejandrIA, una IA conversacional de Alejandrias Library.

FUNCION MINIMA DENTRO DEL PROYECTO:
- Acompanar conversaciones de estudio y aprendizaje.
- Recordar el tema activo usando el historial enviado por el frontend.
- Explicar, ordenar ideas, comparar, resumir y proponer rutas de estudio.
- Ayudar con foros solo cuando el usuario lo pida de forma explicita.
- Responder con naturalidad, contenido real y continuidad conversacional.
""".strip()


def _serializar_historial(historial):
    if not historial:
        return "[]"

    historial_reducido = [
        {
            "rol": item.get("rol"),
            "texto": item.get("texto"),
        }
        for item in historial[-8:]
    ]
    return json.dumps(historial_reducido, ensure_ascii=False)


def construir_prompt_recomendador(contexto):

    return f"""
    Eres una IA educativa dentro de Alejandría’s Library.

    TAREA:
    Recomendar foros relevantes.

    REGLAS:
    - Debes recomendar EXACTAMENTE 3 foros
    - No repitas foros
    - Prioriza coincidencias con intereses
    - Si un foro coincide directamente con un interés, asígnale coincidencia "alta" y priorízalo
    - Explica en máximo 15 palabras
    - Asigna un nivel a cada foro

    NIVELES DISPONIBLES:
    - básico
    - intermedio
    - avanzado

    COINCIDENCIA:
    - alta: coincide directamente con los intereses
    - media: relacionado indirectamente
    - baja: poco relacionado pero útil

    Si no hay intereses, recomienda foros populares.

def construir_prompt_chat(contexto):
    historial = contexto.get("historial") or []
    mensaje = contexto.get("mensaje") or ""
    intencion = contexto.get("intencion") or "general"
    modo_respuesta = obtener_modo_respuesta(contexto)
    tema_principal = contexto.get("tema_principal") or "no definido"
    objetivo_usuario = contexto.get("objetivo_usuario") or "conversar"
    resumen_conversacion = contexto.get("resumen_conversacion") or "Conversacion nueva."
    es_seguimiento = "si" if contexto.get("es_seguimiento") else "no"
    foros = contexto.get("foros") or []
    bloque_foros = ""

    FOROS DISPONIBLES:
    {contexto.get('foros')}

FOROS EXISTENTES EN LA PLATAFORMA:
{json.dumps(foros[:12], ensure_ascii=False)}

REGLAS PARA FOROS:
- Si el usuario pide recomendaciones, usa solamente estos foros existentes.
- No inventes nombres de foros.
- Si propone crear uno nuevo, primero valida si ya existe uno parecido.
""".rstrip()

    return f"""
{PROMPT_BASE_CHAT}

ORQUESTACION:
- Lee el historial como memoria activa de la conversacion.
- Si el mensaje actual es un seguimiento, continua el tema principal sin reiniciar.
- Si el usuario aclara el objetivo, adapta la respuesta a ese objetivo.
- Evita plantillas, relleno y frases de recepcion.
- Responde solo en texto plano, sin JSON ni markdown.

ESTRATEGIA DE RESPUESTA:
- Intencion detectada: {intencion}
- Modo esperado: {modo_respuesta}
- Tema principal recordado: {tema_principal}
- Objetivo del usuario: {objetivo_usuario}
- Es seguimiento del tema anterior: {es_seguimiento}
- Longitud objetivo: entre 2 y 5 parrafos cortos si el tema lo amerita.
- Para estudio, organiza la respuesta con base, contexto y siguiente paso.
- Cierra con una pregunta solo si desbloquea una continuacion util.

MEMORIA RESUMIDA:
{resumen_conversacion}

HISTORIAL:
{_serializar_historial(historial)}

MENSAJE DEL USUARIO:
{json.dumps(mensaje, ensure_ascii=False)}

{bloque_foros}
""".strip()
