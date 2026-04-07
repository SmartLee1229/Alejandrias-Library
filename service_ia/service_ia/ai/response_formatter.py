import json

def formatear_respuesta(texto):
    try:
        data = json.loads(texto)

        # Validación básica
        if not isinstance(data, list):
            return {"error": "Formato incorrecto"}

        return data

    except Exception as e:
        return {
            "error": "No se pudo parsear JSON",
            "raw": texto
        }