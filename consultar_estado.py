import requests
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConsultarEstadoService:
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

            logger.info(f"Solicitando token OAuth2 para consulta estado: {url}")

            response = requests.post(url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                logger.info("Token OAuth2 obtenido exitosamente para consulta estado")
                return self.token
            else:
                error_msg = f"Error obteniendo token para consulta: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión obteniendo token para consulta: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado obteniendo token para consulta: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def consultar_estado_siniestro(self,
                                         id_siniestro: str,
                                         p_cod_cia: str,
                                         p_cod_secc: str,
                                         p_cod_producto: str,
                                         p_entidad_colocadora: str,
                                         p_proceso: str,
                                         p_sistema_origen: str) -> Dict[str, Any]:
        """
        Consulta el estado de un siniestro específico
        """
        try:
            # Asegurar que tenemos un token válido
            if not self.token:
                await self.obtener_token()

            # Construir URL con query parameters
            url = f"{self.base_url}/poliza_siniestros/api/v1/proceso/estado"

            # Parámetros de consulta
            params = {
                "id": id_siniestro
            }

            # Headers con token y parámetros requeridos
            headers = {
                "Authorization": f"Bearer {self.token}",
                "p_cod_cia": p_cod_cia,
                "p_cod_secc": p_cod_secc,
                "p_cod_producto": p_cod_producto,
                "p_entidad_colocadora": p_entidad_colocadora,
                "p_proceso": p_proceso,
                "p_sistema_origen": p_sistema_origen
            }

            logger.info(f"Consultando estado de siniestro ID: {id_siniestro}")
            logger.info(f"URL: {url}")
            logger.info(f"Headers: {dict((k, v) for k, v in headers.items() if k != 'Authorization')}")

            response = requests.get(url, params=params, headers=headers, timeout=30)

            if response.status_code == 200:
                resultado = response.json()
                logger.info(f"Estado consultado exitosamente para ID: {id_siniestro}")
                return resultado
            elif response.status_code == 401:
                # Token expirado, intentar renovar
                logger.warning("Token expirado en consulta estado, renovando...")
                await self.obtener_token()
                headers["Authorization"] = f"Bearer {self.token}"

                # Reintentar
                response = requests.get(url, params=params, headers=headers, timeout=30)
                if response.status_code == 200:
                    resultado = response.json()
                    logger.info(f"Estado consultado exitosamente tras renovar token para ID: {id_siniestro}")
                    return resultado
                else:
                    error_msg = f"Error consultando estado tras renovar token: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            elif response.status_code == 404:
                error_msg = f"Siniestro no encontrado con ID: {id_siniestro}"
                logger.warning(error_msg)
                raise Exception(error_msg)
            else:
                error_msg = f"Error consultando estado: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión consultando estado: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado consultando estado: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def procesar_consulta_estado(self, parametros_consulta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal que orquesta la consulta de estado
        """
        try:
            logger.info(f"Iniciando consulta de estado para ID: {parametros_consulta.get('id')}")

            # Extraer parámetros
            id_siniestro = parametros_consulta.get("id")
            p_cod_cia = parametros_consulta.get("p_cod_cia")
            p_cod_secc = parametros_consulta.get("p_cod_secc")
            p_cod_producto = parametros_consulta.get("p_cod_producto")
            p_entidad_colocadora = parametros_consulta.get("p_entidad_colocadora")
            p_proceso = parametros_consulta.get("p_proceso")
            p_sistema_origen = parametros_consulta.get("p_sistema_origen")

            # Validar parámetros requeridos
            if not all([id_siniestro, p_cod_cia, p_cod_secc, p_cod_producto,
                        p_entidad_colocadora, p_proceso, p_sistema_origen]):
                raise Exception("Faltan parámetros requeridos para la consulta")

            # Paso 1: Obtener token de autenticación
            await self.obtener_token()

            # Paso 2: Consultar estado
            resultado = await self.consultar_estado_siniestro(
                id_siniestro=id_siniestro,
                p_cod_cia=p_cod_cia,
                p_cod_secc=p_cod_secc,
                p_cod_producto=p_cod_producto,
                p_entidad_colocadora=p_entidad_colocadora,
                p_proceso=p_proceso,
                p_sistema_origen=p_sistema_origen
            )

            logger.info(f"Consulta de estado completada exitosamente para ID: {id_siniestro}")

            return {
                "id_consultado": id_siniestro,
                "parametros_consulta": {
                    "p_cod_cia": p_cod_cia,
                    "p_cod_secc": p_cod_secc,
                    "p_cod_producto": p_cod_producto,
                    "p_entidad_colocadora": p_entidad_colocadora,
                    "p_proceso": p_proceso,
                    "p_sistema_origen": p_sistema_origen
                },
                "resultado_api": resultado,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error en consulta de estado: {str(e)}")
            raise Exception(f"Error consultando estado: {str(e)}")