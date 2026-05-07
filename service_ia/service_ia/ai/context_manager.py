import re
import unicodedata

from .conversation import enriquecer_contexto_conversacion


def _limpiar_texto(valor):
    return " ".join(str(valor or "").strip().split())


def _normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", _limpiar_texto(valor))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return texto.lower()


def _normalizar_historial(historial, limite=8):
    if not isinstance(historial, list):
        return []

    normalizado = []
    for item in historial[-limite:]:
        if not isinstance(item, dict):
            continue

        rol = item.get("rol")
        if rol not in {"usuario", "asistente"}:
            continue

        texto = _limpiar_texto(item.get("texto"))
        if not texto:
            continue

        normalizado.append(
            {
                "rol": rol,
                "texto": texto,
            }
        )

    return normalizado


def _detectar_intencion_chat(mensaje):
    texto = _normalizar_texto(mensaje)
    tokens = re.findall(r"[a-z0-9]+", texto)

    if not texto:
        return "general"

    if any(palabra in texto for palabra in ["recomienda", "recomend", "sugiere"]):
        return "recomendacion"
    if any(
        palabra in texto
        for palabra in ["explica", "que es", "que fue", "quien fue", "hablame de", "ensename", "ensena"]
    ):
        return "explicacion"
    if any(palabra in texto for palabra in ["resume", "resumen", "sintetiza"]):
        return "resumen"
    if any(palabra in texto for palabra in ["compara", "diferencia", "versus", "vs"]):
        return "comparacion"
    if texto.endswith("?"):
        return "pregunta"
    if len(tokens) <= 3 and any(token in texto for token in ["historia", "grecia", "roma", "alejandro", "estudios"]):
        return "explicacion"

    return "general"


def construir_contexto(data):
    data = data or {}
    contenido = data.get("data") if isinstance(data.get("data"), dict) else data
    mensaje = _limpiar_texto(contenido.get("mensaje"))
    historial = _normalizar_historial(contenido.get("historial", []))
    foros = contenido.get("foros") or []

    contexto = {
        "intereses": contenido.get("intereses") or [],
        "foros": foros if isinstance(foros, list) else [],
        "historial": historial,
        "mensaje": mensaje,
        "intencion": _detectar_intencion_chat(mensaje),
    }

    return enriquecer_contexto_conversacion(contexto)
