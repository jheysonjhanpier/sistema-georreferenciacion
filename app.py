from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import folium
from folium import plugins
import os
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_coordinates(coord_string):
    """
    Parsea diferentes formatos de coordenadas:
    - "lat, lon"
    - "lat,lon"
    - "(lat, lon)"
    """
    try:
        # Eliminar paréntesis y espacios extras
        coord_string = str(coord_string).strip().replace('(', '').replace(')', '')
        
        # Separar por coma
        parts = coord_string.split(',')
        
        if len(parts) == 2:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            
            # Validar rango de coordenadas
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        
        return None
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Leer el archivo Excel
            df = pd.read_excel(filepath)
            
            # Verificar que tenga las columnas necesarias
            if len(df.columns) < 2:
                flash('El archivo debe tener al menos 2 columnas (Descripción y Coordenadas)', 'error')
                return redirect(url_for('index'))
            
            # Usar las primeras dos columnas
            df.columns = ['descripcion', 'coordenadas'] + list(df.columns[2:])
            
            # Procesar coordenadas
            locations = []
            errores = 0
            
            for idx, row in df.iterrows():
                coords = parse_coordinates(row['coordenadas'])
                if coords:
                    locations.append({
                        'descripcion': str(row['descripcion']),
                        'lat': coords[0],
                        'lon': coords[1]
                    })
                else:
                    errores += 1
            
            if not locations:
                flash('No se encontraron coordenadas válidas en el archivo', 'error')
                return redirect(url_for('index'))
            
            # Crear mapa
            map_center = [locations[0]['lat'], locations[0]['lon']]
            mapa = folium.Map(
                location=map_center,
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcadores
            for loc in locations:
                folium.Marker(
                    location=[loc['lat'], loc['lon']],
                    popup=folium.Popup(loc['descripcion'], max_width=300),
                    tooltip=loc['descripcion'],
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(mapa)
            
            # Agregar control de pantalla completa
            plugins.Fullscreen().add_to(mapa)
            
            # Guardar mapa
            map_path = os.path.join('static', 'mapa.html')
            os.makedirs('static', exist_ok=True)
            mapa.save(map_path)
            
            if errores > 0:
                flash(f'Mapa generado con {len(locations)} ubicaciones. {errores} coordenadas fueron ignoradas por formato incorrecto.', 'warning')
            else:
                flash(f'Mapa generado exitosamente con {len(locations)} ubicaciones', 'success')
            
            return redirect(url_for('show_map'))
            
        except Exception as e:
            flash(f'Error al procesar el archivo: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    flash('Formato de archivo no permitido. Use archivos .xlsx o .xls', 'error')
    return redirect(url_for('index'))

@app.route('/mapa')
def show_map():
    return render_template('mapa.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
