# 🗺️ Sistema de Georreferenciación con Python

Sistema web para visualizar ubicaciones en un mapa interactivo a partir de un archivo Excel con coordenadas.

## 📋 Requisitos Previos

- Python 3.8 o superior instalado
- Visual Studio Code (instalado)
- Conexión a Internet (para descargar librerías)

## 🚀 Instalación

### Paso 1: Abrir el proyecto en Visual Studio Code

1. Abre Visual Studio Code
2. Ve a `Archivo` → `Abrir Carpeta`
3. Selecciona la carpeta donde descargaste estos archivos

### Paso 2: Instalar las dependencias

Abre la terminal en VS Code (Ctrl + ñ o View → Terminal) y ejecuta:

```bash
pip install -r requirements.txt
```

Si tienes problemas con pip, intenta:

```bash
python -m pip install -r requirements.txt
```

O en algunos sistemas:

```bash
pip3 install -r requirements.txt
```

## ▶️ Ejecutar la aplicación

1. En la terminal de VS Code, ejecuta:

```bash
python app.py
```

2. Verás un mensaje como:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.X:5000
```

3. Abre tu navegador web y ve a: `http://localhost:5000`

## 📊 Preparar tu archivo Excel

Tu archivo Excel debe tener **2 columnas**:

1. **Primera columna**: Descripción del lugar
2. **Segunda columna**: Coordenadas en formato `latitud, longitud`

### Ejemplo:

| Descripcion | Coordenadas |
|-------------|-------------|
| Plaza de Armas de Cajamarca | -7.163056, -78.516944 |
| Baños del Inca | -7.163611, -78.463056 |
| Ventanillas de Otuzco | -7.096667, -78.538889 |

**Nota**: Se incluye un archivo `ejemplo_coordenadas.xlsx` que puedes usar para probar.

## 🎯 Cómo usar la aplicación

1. Abre la aplicación en tu navegador (`http://localhost:5000`)
2. Haz clic en el área de carga o arrastra tu archivo Excel
3. Haz clic en "Generar Mapa"
4. ¡Visualiza tus ubicaciones en el mapa interactivo!

## 🌍 Obtener coordenadas

Para obtener coordenadas de lugares:

1. Ve a Google Maps (https://www.google.com/maps)
2. Haz clic derecho en el lugar que te interesa
3. Selecciona las coordenadas que aparecen (primer elemento del menú)
4. Se copiarán en formato: `-7.163056, -78.516944`
5. Pégalas en tu Excel

## 📁 Estructura del Proyecto

```
proyecto/
│
├── app.py                      # Aplicación principal Flask
├── requirements.txt            # Dependencias de Python
├── ejemplo_coordenadas.xlsx    # Archivo de ejemplo
├── README.md                   # Este archivo
│
├── templates/                  # Plantillas HTML
│   ├── index.html             # Página principal
│   └── mapa.html              # Página del mapa
│
├── static/                     # Archivos estáticos (se crea automáticamente)
│   └── mapa.html              # Mapa generado
│
└── uploads/                    # Archivos subidos (se crea automáticamente)
```

## 🛠️ Características

- ✅ Carga de archivos Excel (.xlsx, .xls)
- ✅ **Base de datos SQLite para persistencia de coordenadas**
- ✅ **Visualización de ubicaciones guardadas en tiempo real**
- ✅ **CRUD completo de ubicaciones (Crear, Leer, Actualizar, Eliminar)**
- ✅ Validación de coordenadas
- ✅ Mapa interactivo con marcadores
- ✅ Tooltips y popups con descripciones
- ✅ Diseño responsive y moderno
- ✅ Manejo de errores
- ✅ Pantalla completa en el mapa
- ✅ API REST para integración

## 🔌 API REST Endpoints

La aplicación incluye una API REST para gestionar ubicaciones:

### GET - Obtener todas las ubicaciones
```bash
curl http://localhost:5000/api/ubicaciones
```
**Respuesta:**
```json
[
  {
    "id": 1,
    "descripcion": "Plaza de Armas",
    "lat": -7.163056,
    "lon": -78.516944,
    "archivo_origen": "ejemplo.xlsx",
    "fecha_carga": "2024-12-02T10:30:00"
  }
]
```

### GET - Obtener una ubicación por ID
```bash
curl http://localhost:5000/api/ubicaciones/1
```

### POST - Crear una nueva ubicación
```bash
curl -X POST http://localhost:5000/api/ubicaciones \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Lugar nuevo",
    "latitud": -7.163056,
    "longitud": -78.516944,
    "archivo_origen": "manual"
  }'
```

### PUT - Actualizar una ubicación
```bash
curl -X PUT http://localhost:5000/api/ubicaciones/1 \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Nuevo nombre",
    "latitud": -7.163056,
    "longitud": -78.516944
  }'
```

### DELETE - Eliminar una ubicación
```bash
curl -X DELETE http://localhost:5000/api/ubicaciones/1
```

### GET - Obtener ubicaciones por archivo origen
```bash
curl http://localhost:5000/api/ubicaciones/archivo/ejemplo.xlsx
```

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
Ejecuta de nuevo: `pip install -r requirements.txt`

### Error: "Address already in use"
El puerto 5000 está ocupado. Cambia el puerto en `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambia 5000 a 5001
```

### El archivo no se procesa correctamente
Verifica que tu Excel tenga exactamente 2 columnas y que las coordenadas estén en formato: `latitud, longitud`

## 💾 Base de Datos

La aplicación utiliza **SQLite** para almacenar las coordenadas de forma persistente.

### Archivo de Base de Datos
- Ubicación: `georreferenciacion.db` (se crea automáticamente en la raíz del proyecto)

### Estructura de la Tabla `ubicaciones`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Identificador único |
| descripcion | String(255) | Nombre o descripción del lugar |
| latitud | Float | Coordenada de latitud |
| longitud | Float | Coordenada de longitud |
| archivo_origen | String(255) | Nombre del archivo de origen |
| fecha_carga | DateTime | Fecha y hora de carga |

### Ventajas del Sistema Actual
- ✅ Los datos se guardan automáticamente al cargar un archivo Excel
- ✅ Las ubicaciones persisten entre sesiones
- ✅ Puedes editar, eliminar y agregar ubicaciones manualmente
- ✅ API REST disponible para integración con otras aplicaciones

## 📞 Notas Adicionales

- Las coordenadas deben estar en formato decimal (no grados/minutos/segundos)
- La latitud debe estar entre -90 y 90
- La longitud debe estar entre -180 y 180
- El sistema acepta varios formatos: `-7.163056, -78.516944` o `(-7.163056, -78.516944)`
- **NUEVO**: Todas las ubicaciones se guardan en la base de datos SQLite automáticamente

## 🔒 Seguridad

Para producción, recuerda:
- Cambiar `app.secret_key` en app.py
- Configurar `debug=False`
- Usar un servidor web apropiado (Gunicorn, uWSGI)

---

¡Listo para usar! 🎉
