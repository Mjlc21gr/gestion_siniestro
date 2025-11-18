import requests
import os
import logging
from datetime import datetime
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)


class CrearSiniestroService:
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

            logger.info(f"Solicitando token OAuth2 a: {url}")

            response = requests.post(url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                logger.info("Token OAuth2 obtenido exitosamente")
                return self.token
            else:
                error_msg = f"Error obteniendo token: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión obteniendo token: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado obteniendo token: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def crear_siniestro_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía la solicitud para crear el siniestro a la API de Seguros Bolívar
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

            logger.info(f"Creando siniestro en: {url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200 or response.status_code == 201:
                resultado = response.json()
                logger.info(f"Siniestro creado exitosamente: {resultado}")
                return resultado
            elif response.status_code == 401:
                # Token expirado, intentar renovar
                logger.warning("Token expirado, renovando...")
                await self.obtener_token()
                headers["Authorization"] = f"Bearer {self.token}"

                # Reintentar
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200 or response.status_code == 201:
                    resultado = response.json()
                    logger.info(f"Siniestro creado exitosamente tras renovar token: {resultado}")
                    return resultado
                else:
                    error_msg = f"Error creando siniestro tras renovar token: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                error_msg = f"Error creando siniestro: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión creando siniestro: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado creando siniestro: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def procesar_siniestro(self, payload_completo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal que orquesta todo el proceso de creación del siniestro
        Recibe el payload completo y lo envía directamente a la API
        """
        try:
            logger.info("Iniciando proceso de creación de siniestro")

            # Paso 1: Obtener token de autenticación
            await self.obtener_token()

            # Paso 2: El payload ya viene completo, solo enviarlo
            logger.info(f"Payload recibido: {json.dumps(payload_completo, indent=2)}")

            # Paso 3: Crear el siniestro
            resultado = await self.crear_siniestro_api(payload_completo)

            logger.info("Proceso de creación de siniestro completado exitosamente")

            return {
                "transaccion": payload_completo.get("transaccion"),
                "nro_documento": payload_completo.get("nro_documento"),
                "num_pol1": payload_completo.get("num_pol1"),
                "resultado_api": resultado,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error en proceso de creación de siniestro: {str(e)}")
            raise Exception(f"Error procesando siniestro: {str(e)}")