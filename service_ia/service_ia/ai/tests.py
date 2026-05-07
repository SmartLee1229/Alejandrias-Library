from django.test import TestCase

from django.test import RequestFactory, SimpleTestCase

from .chat_logic import construir_respuesta_foros, es_peticion_de_foros
from .context_manager import construir_contexto
from .orchestrator import preparar_ejecucion
from .views import chat_view


VIEW_MODULE = f"{chat_view.__module__}.generar_texto"
ORCHESTRATOR_MODULE = f"{preparar_ejecucion.__module__}.obtener_foros_existentes"


class OrquestacionIATests(SimpleTestCase):
    def test_contexto_chat_normaliza_historial_e_intencion(self):
        contexto = construir_contexto(
            {
                "tipo": "chat",
                "data": {
                    "mensaje": "   Que fue la antigua Roma?   ",
                    "historial": [
                        {"rol": "asistente", "texto": "Hola"},
                        {"rol": "usuario", "texto": "   Ensename historia  "},
                        {"rol": "otro", "texto": "ignorar"},
                    ],
                },
            }
        )

        self.assertEqual(contexto["mensaje"], "Que fue la antigua Roma?")
        self.assertEqual(contexto["intencion"], "explicacion")
        self.assertEqual(
            contexto["historial"],
            [
                {"rol": "asistente", "texto": "Hola"},
                {"rol": "usuario", "texto": "Ensename historia"},
            ],
        )

    def test_contexto_detecta_explicacion_en_quien_fue(self):
        contexto = construir_contexto(
            {
                "tipo": "chat",
                "data": {
                    "mensaje": "Quien fue Carlos Augusto",
                    "historial": [],
                },
            }
        )

        self.assertEqual(contexto["intencion"], "explicacion")

    def test_contexto_detecta_tema_corto_como_explicacion(self):
        contexto = construir_contexto(
            {
                "tipo": "chat",
                "data": {
                    "mensaje": "alejandro magno",
                    "historial": [],
                },
            }
        )

        self.assertEqual(contexto["intencion"], "explicacion")
        self.assertEqual(contexto["tema_principal"], "alejandro magno")

    def test_contexto_recuerda_tema_en_turno_de_seguimiento(self):
        contexto = construir_contexto(
            {
                "tipo": "chat",
                "data": {
                    "mensaje": "En esta ocasion es solo para estudio",
                    "historial": [
                        {"rol": "usuario", "texto": "Quiero aprender sobre la historia de la antigua roma"},
                        {"rol": "asistente", "texto": "Claro, empecemos por la Roma antigua."},
                    ],
                },
            }
        )

        self.assertEqual(contexto["tema_principal"], "la historia de la antigua Roma")
        self.assertEqual(contexto["objetivo_usuario"], "estudio")
        self.assertTrue(contexto["es_seguimiento"])

    def test_orquestador_chat_construye_prompt_rico(self):
        ejecucion = preparar_ejecucion(
            {
                "tipo": "chat",
                "data": {
                    "mensaje": "Explica la antigua Roma",
                    "historial": [{"rol": "usuario", "texto": "Quiero aprender historia"}],
                },
            }
        )

        self.assertEqual(ejecucion["tarea"], "chat_texto")
        self.assertIn("ORQUESTACION:", ejecucion["prompt"])
        self.assertIn("Intencion detectada: explicacion", ejecucion["prompt"])
        self.assertIn("Tema principal recordado", ejecucion["prompt"])

    def test_respuesta_foros_recomienda_existentes(self):
        respuesta = construir_respuesta_foros(
            {"mensaje": "Recomiendame foros sobre roma antigua", "historial": []},
            [
                {
                    "titulo": "Historia de Roma",
                    "descripcion": "Debates sobre republica e imperio romano",
                    "categoria": "Historia",
                },
                {
                    "titulo": "Egipto antiguo",
                    "descripcion": "Conversaciones sobre faraones y templos",
                    "categoria": "Historia",
                },
            ],
        )

        self.assertIn("Historia de Roma", respuesta)
        self.assertNotIn("invent", respuesta.lower())

    def test_respuesta_foros_creacion_no_depende_de_backend(self):
        respuesta = construir_respuesta_foros(
            {
                "mensaje": "ayudame a definir el titulo del foro",
                "historial": [
                    {"rol": "usuario", "texto": "Me ayudarias a crear un foro sobre la antigua grecia con sus creencias"}
                ],
            },
            [],
        )

        self.assertIn("titulo", respuesta.lower())
        self.assertIn("grecia", respuesta.lower())
        self.assertNotIn("no pude cargar", respuesta.lower())

    def test_es_peticion_de_foros_no_se_pega_por_historial(self):
        contexto = {
            "mensaje": "quien fue cleopatra",
            "historial": [
                {"rol": "usuario", "texto": "que foros me recomiendas?"},
                {"rol": "asistente", "texto": "Estos foros existentes te pueden servir mejor..."},
            ],
        }
        self.assertFalse(es_peticion_de_foros(contexto))

    @patch(VIEW_MODULE, return_value="Te recomiendo Historia de Roma.")
    @patch(ORCHESTRATOR_MODULE)
    def test_chat_view_envia_foros_existentes_a_gemini(self, obtener_foros_existentes, generar_texto):
        obtener_foros_existentes.return_value = [
            {
                "id": 1,
                "titulo": "Historia de Roma",
                "descripcion": "Debates sobre republica e imperio romano",
                "categoria": "Historia",
                "creador": "admin",
                "privado": False,
            }
        ]

        request = RequestFactory().post(
            "/api/ia/chat/",
            data='{"tipo":"chat","data":{"mensaje":"Recomiendame foros sobre roma"}}',
            content_type="application/json",
        )

        response = chat_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"origen": "modelo"', response.content)
        self.assertIn(b"Historia de Roma", response.content)
        generar_texto.assert_called_once()
        prompt = generar_texto.call_args.args[0]
        self.assertIn("FOROS EXISTENTES EN LA PLATAFORMA", prompt)
        self.assertIn("Historia de Roma", prompt)

    @patch(ORCHESTRATOR_MODULE)
    def test_orquestador_recomendador_carga_foros_si_no_vienen_en_payload(self, obtener_foros_existentes):
        obtener_foros_existentes.return_value = [
            {
                "id": 1,
                "titulo": "Historia de Roma",
                "descripcion": "Debates sobre republica e imperio romano",
                "categoria": "Historia",
                "creador": "admin",
                "privado": False,
            }
        ]

        ejecucion = preparar_ejecucion(
            {
                "tipo": "recomendador",
                "data": {
                    "intereses": ["roma"],
                },
            }
        )

        self.assertEqual(ejecucion["tarea"], "recomendar_foros")
        self.assertIn("Historia de Roma", ejecucion["prompt"])

    @patch(VIEW_MODULE, side_effect=RuntimeError("sin red"))
    @patch(ORCHESTRATOR_MODULE)
    def test_chat_view_creacion_foro_usa_respaldo_util_si_modelo_falla(self, obtener_foros_existentes, generar_texto):
        obtener_foros_existentes.return_value = []

        request = RequestFactory().post(
            "/api/ia/chat/",
            data=(
                '{"tipo":"chat","data":{"mensaje":"ayudame a definir el titulo del foro",'
                '"historial":[{"rol":"usuario","texto":"Me ayudarias a crear un foro sobre la antigua grecia con sus creencias"}]}}'
            ),
            content_type="application/json",
        )

        response = chat_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"origen": "respaldo"', response.content)
        self.assertIn(b"grecia", response.content.lower())
        self.assertNotIn(b"no pude cargar", response.content.lower())
        generar_texto.assert_called_once()
