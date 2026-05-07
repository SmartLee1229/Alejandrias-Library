import re
import unicodedata


STOPWORDS_TEMA = {
    "a", "acerca", "algo", "algun", "alguna", "algunas", "alguno", "algunos",
    "aprender", "ayuda", "ayudame", "con", "cual", "cuando", "de", "del",
    "dime", "el", "ella", "ellos", "en", "ensename", "esta", "este", "esto",
    "explica", "explicame", "historia", "la", "las", "lo", "los", "me", "mi",
    "para", "por", "que", "quiero", "sobre", "tema", "un", "una", "y",
}

MARCADORES_TEMA = [
    r"\bsobre\s+(.+)$",
    r"\bacerca de\s+(.+)$",
    r"\btema de\s+(.+)$",
    r"\baprender\s+(.+)$",
    r"\bestudiar\s+(.+)$",
    r"\bexplicame\s+(.+)$",
    r"\bexplica\s+(.+)$",
]


def limpiar_texto(valor):
    return " ".join(str(valor or "").strip().split())


def normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", limpiar_texto(valor))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return texto.lower()


def _quitar_cierre(texto):
    return re.split(r"[?.!,;:]", limpiar_texto(texto), maxsplit=1)[0].strip()


def _capitalizar_tema(tema):
    palabras = []
    for palabra in limpiar_texto(tema).split():
        if palabra.lower() in {"roma", "grecia", "egipto"}:
            palabras.append(palabra.capitalize())
        else:
            palabras.append(palabra)
    return " ".join(palabras).strip()


def extraer_tema(texto):
    texto_limpio = limpiar_texto(texto)
    texto_normalizado = normalizar_texto(texto_limpio)

    if not texto_normalizado:
        return ""

    for patron in MARCADORES_TEMA:
        coincidencia = re.search(patron, texto_normalizado)
        if coincidencia:
            tema = _quitar_cierre(coincidencia.group(1))
            if tema:
                return _capitalizar_tema(tema)

    tokens = re.findall(r"[a-z0-9]+", texto_normalizado)
    utiles = [token for token in tokens if len(token) > 2 and token not in STOPWORDS_TEMA]
    if len(utiles) >= 2:
        return _capitalizar_tema(" ".join(utiles[:6]))

    return ""


def tiene_marcador_tema(texto):
    texto_normalizado = normalizar_texto(texto)
    return any(re.search(patron, texto_normalizado) for patron in MARCADORES_TEMA)


def es_turno_de_seguimiento(mensaje):
    texto = normalizar_texto(mensaje)
    if not texto:
        return False

    if len(texto.split()) <= 8:
        return True

    marcadores = [
        "en esta ocasion",
        "esta vez",
        "solo para",
        "sigamos",
        "continua",
        "continuemos",
        "lo anterior",
        "ese tema",
        "este tema",
        "entonces",
        "tambien",
    ]
    return any(marcador in texto for marcador in marcadores)


def detectar_objetivo(mensaje, historial=None):
    texto = normalizar_texto(mensaje)
    historial_texto = normalizar_texto(" ".join(item.get("texto", "") for item in (historial or [])))
    combinado = f"{historial_texto} {texto}"

    if any(palabra in combinado for palabra in ["foro", "foros", "comunidad"]):
        if any(palabra in texto for palabra in ["recomienda", "sugiere", "crear", "titulo", "descripcion"]):
            return "foros"

    if any(palabra in texto for palabra in ["estudio", "estudiar", "aprender", "examen", "clase"]):
        return "estudio"

    if any(palabra in texto for palabra in ["compar", "diferencia", "versus", " vs "]):
        return "comparar"

    if any(palabra in texto for palabra in ["resume", "resumen", "sintetiza"]):
        return "resumir"

    return "conversar"


def enriquecer_contexto_conversacion(contexto):
    contexto = dict(contexto or {})
    mensaje = contexto.get("mensaje") or ""
    historial = contexto.get("historial") or []
    tema_actual = extraer_tema(mensaje)

    temas_historial = [
        extraer_tema(item.get("texto", ""))
        for item in historial
        if item.get("rol") == "usuario" and item.get("texto") != mensaje
    ]
    temas_historial = [tema for tema in temas_historial if tema]

    if temas_historial and es_turno_de_seguimiento(mensaje) and not tiene_marcador_tema(mensaje):
        tema_actual = ""

    tema_principal = tema_actual or (temas_historial[-1] if temas_historial else "")
    objetivo = detectar_objetivo(mensaje, historial)
    es_seguimiento = bool(tema_principal and not tema_actual and es_turno_de_seguimiento(mensaje))

    contexto["tema_principal"] = tema_principal
    contexto["objetivo_usuario"] = objetivo
    contexto["es_seguimiento"] = es_seguimiento
    contexto["resumen_conversacion"] = construir_resumen_conversacion(historial, tema_principal, objetivo)
    return contexto


def construir_resumen_conversacion(historial, tema_principal="", objetivo="conversar"):
    mensajes_usuario = [
        limpiar_texto(item.get("texto", ""))
        for item in (historial or [])
        if item.get("rol") == "usuario" and limpiar_texto(item.get("texto", ""))
    ]

    if not mensajes_usuario:
        return "Conversacion nueva."

    base = f"Tema principal: {tema_principal or 'aun no definido'}. Objetivo actual: {objetivo}."
    ultimos = " | ".join(mensajes_usuario[-3:])
    return f"{base} Ultimos mensajes del usuario: {ultimos}"


def construir_respuesta_respaldo(contexto):
    mensaje = limpiar_texto((contexto or {}).get("mensaje"))
    tema = limpiar_texto((contexto or {}).get("tema_principal"))
    objetivo = (contexto or {}).get("objetivo_usuario") or "conversar"

    if not mensaje:
        return "Estoy listo. Escribe tu pregunta y sigo el hilo contigo."

    texto = normalizar_texto(mensaje)
    if any(saludo in texto for saludo in ["hola", "buenas", "hey"]):
        return (
            "Hola. Soy AlejandrIA, tu asistente de estudio dentro de Alejandrias Library. "
            "Puedo ayudarte a aprender, ordenar ideas y convertir temas en explicaciones claras."
        )

    if tema and objetivo == "estudio":
        return (
            f"Perfecto, seguimos con {tema} en modo estudio. Para empezar con una base clara, "
            f"conviene verlo en tres niveles: primero, que estaba pasando antes y por que {tema} "
            "se vuelve importante; segundo, cuales fueron sus instituciones, personajes o ideas clave; "
            "tercero, que legado dejo y como se nota despues. "
            "Si quieres estudiar con orden, arrancaria por una linea de tiempo breve y despues pasaria "
            "a causas, consecuencias y ejemplos concretos."
        )

    if tema:
        return (
            f"Sigamos con {tema}. Lo importante es no tratarlo como un dato aislado: hay que ubicarlo "
            "en contexto, separar sus ideas principales y cerrar con un ejemplo. "
            "Puedo desarrollarlo como explicacion, resumen, linea de tiempo o guia de estudio."
        )

    return (
        f"Entiendo tu mensaje: {mensaje}. Para responderlo bien necesito fijar el tema central; "
        "si me das una palabra clave o el objetivo, puedo convertirlo en una explicacion clara y seguida."
    )
