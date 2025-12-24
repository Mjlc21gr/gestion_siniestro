import requests
import os
import logging
from datetime import datetime
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)


class ModificacionReservaService:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "https://stg-api-conecta.segurosbolivar.com/stage")
        self.client_id = os.getenv("CLIENT_ID", "42qjqldt7tp19ja02pjrfhhco")
        self.client_secret = os.getenv("CLIENT_SECRET", "quep14jpdaen4lngtj0rk8nvh7nv3sl2g0u2e5qh40cpgvti10q")
        self.token = None

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

            logger.info(f"Solicitando token OAuth2 para modificación de reserva: {url}")

            response = requests.post(url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                logger.info("Token OAuth2 obtenido exitosamente para modificación de reserva")
                return self.token
            else:
                error_msg = f"Error obteniendo token para modificación de reserva: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión obteniendo token para modificación de reserva: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado obteniendo token para modificación de reserva: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def construir_payload_modificacion_reserva(self, datos_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye el payload JSON para la modificación de reserva
        Combina campos fijos con campos dinámicos recibidos del request
        """
        payload = {
            # Campos fijos
            "proceso": 772,
            "entidad_colocadora": 0,
            "sim_sistema_origen": 124,
            "sim_id_canal": 3,
            "sim_usuario_creacion": "B1062816",
            
            # Campos dinámicos del request
            "transaccion": datos_request["transaccion"],
            "cod_cia": datos_request["cod_cia"],
            "cod_secc": datos_request["cod_secc"],
            "num_sini": datos_request["num_sini"],
            "cod_producto": datos_request["cod_producto"],
            
            # Datos del expediente
            "vdatos_expediente": {
                "tipo_exped": datos_request["tipo_exped"],
                "cod_cau_mod_ex": datos_request["cod_cau_mod_ex"],
                "vdatos_reserva": datos_request["vdatos_reserva"]
            }
        }

        return payload

    async def modificar_reserva_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía la solicitud para modificar la reserva a la API de Seguros Bolívar
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

            logger.info(f"Modificando reserva en: {url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200 or response.status_code == 201:
                resultado = response.json()
                logger.info(f"Reserva modificada exitosamente: {resultado}")
                return resultado
            elif response.status_code == 401:
                # Token expirado, intentar renovar
                logger.warning("Token expirado en modificación de reserva, renovando...")
                await self.obtener_token()
                headers["Authorization"] = f"Bearer {self.token}"

                # Reintentar
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200 or response.status_code == 201:
                    resultado = response.json()
                    logger.info(f"Reserva modificada exitosamente tras renovar token: {resultado}")
                    return resultado
                else:
                    error_msg = f"Error modificando reserva tras renovar token: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                error_msg = f"Error modificando reserva: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión modificando reserva: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado modificando reserva: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def procesar_modificacion_reserva(self, datos_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal que orquesta todo el proceso de modificación de reserva
        """
        try:
            logger.info(f"Iniciando proceso de modificación de reserva para siniestro: {datos_request.get('num_sini')}")

            # Paso 1: Obtener token de autenticación
            await self.obtener_token()

            # Paso 2: Construir el payload
            payload = self.construir_payload_modificacion_reserva(datos_request)

            # Paso 3: Modificar la reserva
            resultado = await self.modificar_reserva_api(payload)

            logger.info("Proceso de modificación de reserva completado exitosamente")

            return {
                "transaccion": datos_request["transaccion"],
                "num_sini": datos_request["num_sini"],
                "cod_cia": datos_request["cod_cia"],
                "cod_secc": datos_request["cod_secc"],
                "cod_producto": datos_request["cod_producto"],
                "resultado_api": resultado,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error en proceso de modificación de reserva: {str(e)}")
            raise Exception(f"Error procesando modificación de reserva: {str(e)}")

