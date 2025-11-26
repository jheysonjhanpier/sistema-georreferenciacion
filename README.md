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
- ✅ Validación de coordenadas
- ✅ Mapa interactivo con marcadores
- ✅ Tooltips y popups con descripciones
- ✅ Diseño responsive y moderno
- ✅ Manejo de errores
- ✅ Pantalla completa en el mapa

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

## 📞 Notas Adicionales

- Las coordenadas deben estar en formato decimal (no grados/minutos/segundos)
- La latitud debe estar entre -90 y 90
- La longitud debe estar entre -180 y 180
- El sistema acepta varios formatos: `-7.163056, -78.516944` o `(-7.163056, -78.516944)`

## 🔒 Seguridad

Para producción, recuerda:
- Cambiar `app.secret_key` en app.py
- Configurar `debug=False`
- Usar un servidor web apropiado (Gunicorn, uWSGI)

---

¡Listo para usar! 🎉
