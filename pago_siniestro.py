import requests
import os
import logging
from datetime import datetime
from typing import Dict, Any
import json
import asyncio
from consultar_estado import ConsultarEstadoService

logger = logging.getLogger(__name__)


class PagoSiniestroService:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "https://stg-api-conecta.segurosbolivar.com/stage")
        self.client_id = os.getenv("CLIENT_ID", "42qjqldt7tp19ja02pjrfhhco")
        self.client_secret = os.getenv("CLIENT_SECRET", "quep14jpdaen4lngtj0rk8nvh7nv3sl2g0u2e5qh40cpgvti10q")
        self.token = None
        self.consulta_estado_service = ConsultarEstadoService()

    async def obtener_token(self) -> str:
        """
        Obtiene el token de autenticación OAuth2 desde la API de Seguros Bolívar
        """
        try:
            url = f"{self.base_url}/oauth2/token"

            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

            logger.info(f"Solicitando token OAuth2 para pago siniestro: {url}")

            response = requests.post(url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                logger.info("Token OAuth2 obtenido exitosamente para pago siniestro")
                return self.token
            else:
                error_msg = f"Error obteniendo token para pago: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión obteniendo token para pago: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado obteniendo token para pago: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def construir_payload_pago(self, datos_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye el payload JSON para el pago del siniestro
        Mapea los campos recibidos al formato requerido por la API
        """

        # Mapeo de campos
        # compania -> cod_cia
        # seccion -> cod_secc
        # producto -> cod_producto

        payload = {
            "proceso": "30",
            "entidad_colocadora": "183",
            "sim_sistema_origen": "194",
            "sim_id_canal": "3",
            "transaccion": datos_request["transaccion"],
            "num_sini": datos_request["num_sini"],
            "cod_cia": datos_request["compania"],  # Mapeo: compania -> cod_cia
            "cod_secc": datos_request["seccion"],  # Mapeo: seccion -> cod_secc
            "cod_producto": datos_request["producto"],  # Mapeo: producto -> cod_producto
            "num_pol1": datos_request["num_pol1"],
            "tipo_dec": "D",
            "sim_usuario_creacion": "1022365456",
            "vdatos_liquidacion": {
                "cod_act_benef": datos_request["cod_act_benef"],
                "tdoc_tercero": datos_request["tdoc_tercero"],
                "cod_benef": datos_request["cod_benef"],
                "nro_factura": datos_request["nro_factura"],
                "fecha_factura": datos_request["fecha_factura"],
                "localida_factura": datos_request["localida_factura"],
                "factura_exenta": datos_request["factura_exenta"],
                "con_iva_sim": datos_request["con_iva_sim"],
                "observacion": "PAGO API ",
                "cod_texto": datos_request["cod_texto"],
                "sub_cod_texto": datos_request["sub_cod_texto"],
                "tipo_liq": datos_request["tipo_liq"],
                "total_bruto_liq": datos_request["total_bruto_liq"],
                "autorizante": datos_request["autorizante"],
                "fecha_liq": datos_request["fecha_liq"],
                "cod_pago": datos_request["cod_pago"],
                "cod_mon_liq": datos_request["cod_mon_liq"],
                "sub_tipo_ordpago": datos_request["sub_tipo_ordpago"],
                "vdatos_det_liquidacion": [
                    {
                        "cod_cob": datos_request["cod_cob"],
                        "cod_concep_liq": datos_request["cod_concep_liq"],
                        "importe_liq": datos_request["importe_liq"],
                        "cod_concep_rva": datos_request["cod_concep_rva"]
                    }
                ]
            },
            "vdatos_expediente": {
                "nro_exped": datos_request["nro_exped"],
                "tipo_exped": datos_request["tipo_exped"]
            }
        }

        return payload

    async def procesar_pago_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía la solicitud para procesar el pago del siniestro a la API de Seguros Bolívar
        """
        try:
            # Asegurar que tenemos un token válido
            if not self.token:
                await self.obtener_token()

            url = f"{self.base_url}/poliza_siniestros/api/v1/procesar"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }

            logger.info(f"Procesando pago de siniestro en: {url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200 or response.status_code == 201:
                resultado = response.json()
                logger.info(f"Pago procesado exitosamente: {resultado}")
                return resultado
            elif response.status_code == 401:
                # Token expirado, intentar renovar
                logger.warning("Token expirado en pago, renovando...")
                await self.obtener_token()
                headers["Authorization"] = f"Bearer {self.token}"

                # Reintentar
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200 or response.status_code == 201:
                    resultado = response.json()
                    logger.info(f"Pago procesado exitosamente tras renovar token: {resultado}")
                    return resultado
                else:
                    error_msg = f"Error procesando pago tras renovar token: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                error_msg = f"Error procesando pago: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión procesando pago: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado procesando pago: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def procesar_pago_siniestro(self, datos_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal que orquesta todo el proceso de pago del siniestro
        y automáticamente consulta el estado después de procesar el pago
        """
        try:
            logger.info(f"Iniciando proceso de pago para siniestro: {datos_request.get('num_sini')}")

            # Paso 1: Obtener token de autenticación
            await self.obtener_token()

            # Paso 2: Construir el payload para el pago
            payload = self.construir_payload_pago(datos_request)

            # Paso 3: Procesar el pago
            resultado_pago = await self.procesar_pago_api(payload)

            logger.info("Pago procesado exitosamente, esperando 10 segundos antes de consultar estado...")

            # Paso 4: Esperar 10 segundos para que el sistema procese
            await asyncio.sleep(10)

            # Paso 5: Consultar automáticamente el estado
            logger.info("Consultando estado automáticamente después del pago...")

            # Preparar parámetros para la consulta de estado
            parametros_consulta = {
                "id": datos_request["transaccion"],  # Usar la transacción como ID
                "p_cod_cia": datos_request["compania"],  # Mapeo directo
                "p_cod_secc": datos_request["seccion"],  # Mapeo directo
                "p_cod_producto": datos_request["producto"],  # Mapeo directo
                "p_entidad_colocadora": "183",  # Valor fijo
                "p_proceso": "30",  # Valor fijo para pagos
                "p_sistema_origen": "194"  # Valor fijo
            }

            try:
                # Consultar estado usando el servicio
                resultado_consulta = await self.consulta_estado_service.procesar_consulta_estado(parametros_consulta)

                logger.info("Consulta de estado completada exitosamente después del pago")

                # Retornar directamente el resultado de la consulta de estado
                return resultado_consulta

            except Exception as e_consulta:
                logger.warning(f"Error consultando estado después del pago: {str(e_consulta)}")

                # Si falla la consulta, retornar la respuesta del pago con el error
                return {
                    "pago_procesado": True,
                    "transaccion": payload["transaccion"],
                    "num_sini": datos_request["num_sini"],
                    "num_pol1": datos_request["num_pol1"],
                    "compania_enviada": datos_request["compania"],
                    "seccion_enviada": datos_request["seccion"],
                    "producto_enviado": datos_request["producto"],
                    "resultado_pago": resultado_pago,
                    "consulta_estado": {
                        "success": False,
                        "error": str(e_consulta),
                        "message": "Pago procesado pero falló la consulta automática de estado"
                    },
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error en proceso de pago de siniestro: {str(e)}")
            raise Exception(f"Error procesando pago: {str(e)}")