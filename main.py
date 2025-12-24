from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from crear_siniestro import CrearSiniestroService
from consultar_estado import ConsultarEstadoService
from pago_siniestro import PagoSiniestroService
from modificacion_reserva import ModificacionReservaService

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


# Modelo para variables dinámicas
class VariableDatos(BaseModel):
    cod_modulo: str
    cod_nivel: str
    cod_grupo: str
    cod_campo: str
    valor_campo: str


# Modelo para el request body - JSON completo
class SiniestroRequest(BaseModel):
    proceso: str
    entidad_colocadora: str
    sim_sistema_origen: str
    transaccion: str
    cod_cia: str
    cod_secc: str
    cod_producto: str
    tdoc_tercero_aseg: str
    cod_aseg: str
    tdoc_tercero_tom: str
    nro_documento: str
    num_pol1: str
    cod_ries: str
    cod_causa_sini: str
    fec_denu_sini: str
    fecha_sini: str
    hora_sini: str
    desc_sini: str
    sim_fec_formalizac: str
    sim_usuario_creacion: str
    pol_principal: str
    vdatos_variables: list[VariableDatos]


# Modelo para consulta de estado
class ConsultaEstadoRequest(BaseModel):
    transaccion: str
    p_cod_cia: str
    p_cod_secc: str
    p_cod_producto: str
    p_entidad_colocadora: str
    p_proceso: str
    p_sistema_origen: str


# Modelo para pago de siniestro
class PagoSiniestroRequest(BaseModel):
    transaccion: str
    num_sini: str
    compania: str  # Se mapea a cod_cia
    seccion: str  # Se mapea a cod_secc
    producto: str  # Se mapea a cod_producto
    num_pol1: str
    cod_act_benef: str
    tdoc_tercero: str
    cod_benef: str
    nro_factura: str
    fecha_factura: str
    localida_factura: str
    factura_exenta: str
    con_iva_sim: str
    cod_texto: str
    sub_cod_texto: str
    tipo_liq: str
    total_bruto_liq: int
    autorizante: str
    fecha_liq: str
    cod_pago: int
    cod_mon_liq: int
    sub_tipo_ordpago: str
    cod_cob: str
    cod_concep_liq: int
    importe_liq: int
    cod_concep_rva: int
    nro_exped: str
    tipo_exped: str


# Modelo para datos de reserva
class DatosReserva(BaseModel):
    cod_mon: int
    cod_cob: int
    cod_concep_rva: int
    valor_movim: int


# Modelo para modificación de reserva
class ModificacionReservaRequest(BaseModel):
    transaccion: str
    cod_cia: int
    cod_secc: int
    num_sini: int
    cod_producto: int
    tipo_exped: str
    cod_cau_mod_ex: str
    vdatos_reserva: List[DatosReserva]


# Instanciar los servicios
siniestro_service = CrearSiniestroService()
consulta_estado_service = ConsultarEstadoService()
pago_siniestro_service = PagoSiniestroService()
modificacion_reserva_service = ModificacionReservaService()


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
        logger.info(f"Iniciando creación de siniestro para documento: {request.nro_documento}")

        # Delegar la creación del siniestro al servicio
        resultado = await siniestro_service.procesar_siniestro(request.dict())

        logger.info(f"Siniestro creado exitosamente para documento: {request.nro_documento}")

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


@app.post("/consultar-estado")
async def consultar_estado_siniestro(request: ConsultaEstadoRequest):
    """
    Endpoint para consultar el estado de un siniestro
    Recibe el ID del siniestro y los parámetros requeridos
    """
    try:
        logger.info(f"Iniciando consulta de estado para transacción: {request.transaccion}")

        # Delegar la consulta al servicio
        resultado = await consulta_estado_service.procesar_consulta_estado(request.dict())

        logger.info(f"Consulta de estado completada para transacción: {request.transaccion}")

        return {
            "success": True,
            "message": "Estado consultado exitosamente",
            "data": resultado
        }

    except Exception as e:
        logger.error(f"Error consultando estado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error consultando estado: {str(e)}"
        )


@app.post("/pago-siniestro")
async def pagar_siniestro(request: PagoSiniestroRequest):
    """
    Endpoint para procesar pago de siniestro
    Recibe campos amigables y los transforma a códigos internos
    """
    try:
        logger.info(f"Iniciando pago de siniestro: {request.num_sini}")

        # Delegar el pago al servicio
        resultado = await pago_siniestro_service.procesar_pago_siniestro(request.dict())

        logger.info(f"Pago procesado exitosamente para siniestro: {request.num_sini}")

        return {
            "success": True,
            "message": "Gestion de pago",
            "data": resultado
        }

    except Exception as e:
        logger.error(f"Error procesando pago: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando pago: {str(e)}"
        )


@app.post("/modificacion-reserva")
async def modificar_reserva(request: ModificacionReservaRequest):
    """
    Endpoint para modificar la reserva de un siniestro
    Recibe los datos dinámicos y los combina con valores fijos del sistema
    """
    try:
        logger.info(f"Iniciando modificación de reserva para siniestro: {request.num_sini}")

        # Convertir el request a diccionario
        request_dict = request.dict()
        
        # Convertir los objetos DatosReserva a diccionarios si es necesario
        request_dict["vdatos_reserva"] = [
            reserva if isinstance(reserva, dict) else reserva.dict() 
            for reserva in request_dict["vdatos_reserva"]
        ]

        # Delegar la modificación al servicio
        resultado = await modificacion_reserva_service.procesar_modificacion_reserva(request_dict)

        logger.info(f"Reserva modificada exitosamente para siniestro: {request.num_sini}")

        return {
            "success": True,
            "message": "Reserva modificada exitosamente",
            "data": resultado
        }

    except Exception as e:
        logger.error(f"Error modificando reserva: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error modificando reserva: {str(e)}"
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