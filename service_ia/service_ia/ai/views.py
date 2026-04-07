from rest_framework.decorators import api_view
from rest_framework.response import Response

from .task_router import obtener_tarea
from .prompt_builder import construir_prompt
from .context_manager import construir_contexto
from .response_formatter import formatear_respuesta
from .gemini_client import model


@api_view(['POST'])
def ia_handler(request):

    tipo = request.data.get('tipo')
    data = request.data.get('data', {})

    # 1. decidir tarea
    tarea = obtener_tarea(tipo)

    # 2. construir contexto
    contexto = construir_contexto(data)

    # 3. construir prompt
    prompt = construir_prompt(tarea, contexto)

    # 4. llamar IA
    respuesta = model.generate_content(prompt)

    # 5. formatear salida
    resultado = formatear_respuesta(respuesta.text)

    return Response({
        "ok": True,
        "data": resultado
    })