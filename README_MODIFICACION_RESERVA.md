# API de Gestión de Siniestros - Seguros Bolívar

## Descripción
API REST para gestionar siniestros en el sistema de Seguros Bolívar.

## Endpoints Disponibles

### 1. Crear Siniestro
**POST** `/crear-siniestro`

### 2. Consultar Estado
**POST** `/consultar-estado`

### 3. Pago de Siniestro
**POST** `/pago-siniestro`

### 4. Modificación de Reserva (NUEVO)
**POST** `/modificacion-reserva`

Endpoint para modificar la reserva de un siniestro existente.

#### Request Body
```json
{
    "transaccion": "2330010",
    "cod_cia": 2,
    "cod_secc": 22,
    "num_sini": 10008000825,
    "cod_producto": 735,
    "tipo_exped": "GSO",
    "cod_cau_mod_ex": "92",
    "vdatos_reserva": [
        {
            "cod_mon": 1,
            "cod_cob": 663,
            "cod_concep_rva": 69,
            "valor_movim": 50000
        }
    ]
}
```

#### Campos del Request

**Campos Dinámicos (Enviados en el Request):**
- `transaccion` (string): Identificador de la transacción
- `cod_cia` (int): Código de la compañía
- `cod_secc` (int): Código de la sección
- `num_sini` (int): Número del siniestro
- `cod_producto` (int): Código del producto
- `tipo_exped` (string): Tipo de expediente
- `cod_cau_mod_ex` (string): Código de causa de modificación del expediente
- `vdatos_reserva` (array): Array de objetos con los datos de la reserva
  - `cod_mon` (int): Código de moneda
  - `cod_cob` (int): Código de cobertura
  - `cod_concep_rva` (int): Código de concepto de reserva
  - `valor_movim` (int): Valor del movimiento

**Campos Fijos (Configurados Automáticamente):**
- `proceso`: 772
- `entidad_colocadora`: 0
- `sim_sistema_origen`: 124
- `sim_id_canal`: 3
- `sim_usuario_creacion`: "B1062816"

#### Response Exitoso (200)
```json
{
    "success": true,
    "message": "Reserva modificada exitosamente",
    "data": {
        "transaccion": "2330010",
        "num_sini": 10008000825,
        "cod_cia": 2,
        "cod_secc": 22,
        "cod_producto": 735,
        "resultado_api": {
            // Respuesta de la API de Seguros Bolívar
        },
        "timestamp": "2025-12-24T10:30:00.000000"
    }
}
```

#### Response de Error (500)
```json
{
    "detail": "Error modificando reserva: [mensaje de error]"
}
```

#### Ejemplo de Uso con cURL
```bash
curl -X POST "http://localhost:8080/modificacion-reserva" \
  -H "Content-Type: application/json" \
  -d '{
    "transaccion": "2330010",
    "cod_cia": 2,
    "cod_secc": 22,
    "num_sini": 10008000825,
    "cod_producto": 735,
    "tipo_exped": "GSO",
    "cod_cau_mod_ex": "92",
    "vdatos_reserva": [
        {
            "cod_mon": 1,
            "cod_cob": 663,
            "cod_concep_rva": 69,
            "valor_movim": 50000
        }
    ]
}'
```

#### Ejemplo de Uso con Python
```python
import requests

url = "http://localhost:8080/modificacion-reserva"
payload = {
    "transaccion": "2330010",
    "cod_cia": 2,
    "cod_secc": 22,
    "num_sini": 10008000825,
    "cod_producto": 735,
    "tipo_exped": "GSO",
    "cod_cau_mod_ex": "92",
    "vdatos_reserva": [
        {
            "cod_mon": 1,
            "cod_cob": 663,
            "cod_concep_rva": 69,
            "valor_movim": 50000
        }
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución Local

```bash
python main.py
```

La API estará disponible en: `http://localhost:8080`

## Documentación Interactiva

Una vez que la API esté en ejecución, puedes acceder a la documentación interactiva en:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Variables de Entorno

- `API_BASE_URL`: URL base de la API de Seguros Bolívar (default: staging)
- `CLIENT_ID`: Client ID para autenticación OAuth2
- `CLIENT_SECRET`: Client Secret para autenticación OAuth2

## Despliegue en GCP

El proyecto incluye:
- `Dockerfile`: Para crear la imagen Docker
- `app.yaml`: Configuración para App Engine

## Estructura del Proyecto

```
.
├── main.py                      # API principal con todos los endpoints
├── crear_siniestro.py          # Servicio para crear siniestros
├── consultar_estado.py         # Servicio para consultar estado
├── pago_siniestro.py           # Servicio para procesar pagos
├── modificacion_reserva.py     # Servicio para modificar reservas (NUEVO)
├── requirements.txt            # Dependencias del proyecto
├── Dockerfile                  # Configuración Docker
└── app.yaml                    # Configuración App Engine
```

