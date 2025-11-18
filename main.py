from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import logging
from crear_siniestro import CrearSiniestroService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Crear Siniestros - Seguros Bolívar",
    description="API para crear siniestros en el sistema de Seguros Bolívar",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelo para el request body
class SiniestroRequest(BaseModel):
    numeroDocumento: str
    numeroPoliza: str
    horaSiniestro: str
    pat_Asg: str
    responsabilidad: str
    posRecobro: str
    tipoDocTaller: str
    lesionados: str
    direccionOcurrencia: str
    localidadSiniestro: str
    correoSini: str
    ciudadAtencion: str
    autoridad: str
    descripcionHecho: str
    nitTaller: str
    tipoCobertura: str


# Instanciar el servicio
siniestro_service = CrearSiniestroService()


@app.get("/")
async def root():
    """Endpoint de salud de la API"""
    return {
        "status": "API funcionando correctamente",
        "service": "Crear Siniestros - Seguros Bolívar",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "service": "siniestros-api"}


@app.post("/crear-siniestro")
async def crear_siniestro(request: SiniestroRequest):
    """
    Endpoint principal para crear un siniestro
    Recibe los datos del siniestro y delega la creación al servicio correspondiente
    """
    try:
        logger.info(f"Iniciando creación de siniestro para documento: {request.numeroDocumento}")

        # Delegar la creación del siniestro al servicio
        resultado = await siniestro_service.procesar_siniestro(request.dict())

        logger.info(f"Siniestro creado exitosamente para documento: {request.numeroDocumento}")

        return {
            "success": True,
            "message": "Siniestro creado exitosamente",
            "data": resultado
        }

    except Exception as e:
        logger.error(f"Error creando siniestro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {str(exc)}")
    return {
        "success": False,
        "message": "Error interno del servidor",
        "error": str(exc)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)