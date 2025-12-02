from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import folium
from folium import plugins
import os
from werkzeug.utils import secure_filename
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///georreferenciacion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
db = SQLAlchemy(app)

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Modelo de base de datos para ubicaciones
class Ubicacion(db.Model):
    __tablename__ = 'ubicaciones'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    archivo_origen = db.Column(db.String(255), nullable=True)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'lat': self.latitud,
            'lon': self.longitud,
            'archivo_origen': self.archivo_origen,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else None
        }

# Crear tablas de base de datos
with app.app_context():
    db.create_all()

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

            # Procesar coordenadas y guardar en base de datos
            locations = []
            errores = 0

            for idx, row in df.iterrows():
                coords = parse_coordinates(row['coordenadas'])
                if coords:
                    ubicacion = Ubicacion(
                        descripcion=str(row['descripcion']),
                        latitud=coords[0],
                        longitud=coords[1],
                        archivo_origen=filename
                    )
                    db.session.add(ubicacion)

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

            # Confirmar guardado en base de datos
            db.session.commit()

            # Crear mapa con datos de la base de datos
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
            db.session.rollback()
            flash(f'Error al procesar el archivo: {str(e)}', 'error')
            return redirect(url_for('index'))

    flash('Formato de archivo no permitido. Use archivos .xlsx o .xls', 'error')
    return redirect(url_for('index'))

@app.route('/mapa')
def show_map():
    return render_template('mapa.html')

@app.route('/api/ubicaciones', methods=['GET'])
def get_ubicaciones():
    """Obtener todas las ubicaciones guardadas"""
    try:
        ubicaciones = Ubicacion.query.all()
        return jsonify([loc.to_dict() for loc in ubicaciones])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ubicaciones/<int:id>', methods=['GET'])
def get_ubicacion(id):
    """Obtener una ubicación por ID"""
    try:
        ubicacion = Ubicacion.query.get_or_404(id)
        return jsonify(ubicacion.to_dict())
    except Exception as e:
        return jsonify({'error': 'Ubicación no encontrada'}), 404

@app.route('/api/ubicaciones', methods=['POST'])
def create_ubicacion():
    """Crear una nueva ubicación manualmente"""
    try:
        data = request.get_json()

        if not data or 'descripcion' not in data or 'latitud' not in data or 'longitud' not in data:
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        # Validar coordenadas
        lat = float(data['latitud'])
        lon = float(data['longitud'])

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return jsonify({'error': 'Coordenadas fuera de rango'}), 400

        ubicacion = Ubicacion(
            descripcion=str(data['descripcion']),
            latitud=lat,
            longitud=lon,
            archivo_origen=data.get('archivo_origen', 'Manual')
        )

        db.session.add(ubicacion)
        db.session.commit()

        return jsonify(ubicacion.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ubicaciones/<int:id>', methods=['PUT'])
def update_ubicacion(id):
    """Actualizar una ubicación"""
    try:
        ubicacion = Ubicacion.query.get_or_404(id)
        data = request.get_json()

        if 'descripcion' in data:
            ubicacion.descripcion = str(data['descripcion'])

        if 'latitud' in data and 'longitud' in data:
            lat = float(data['latitud'])
            lon = float(data['longitud'])

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return jsonify({'error': 'Coordenadas fuera de rango'}), 400

            ubicacion.latitud = lat
            ubicacion.longitud = lon

        db.session.commit()
        return jsonify(ubicacion.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ubicaciones/<int:id>', methods=['DELETE'])
def delete_ubicacion(id):
    """Eliminar una ubicación"""
    try:
        ubicacion = Ubicacion.query.get_or_404(id)
        db.session.delete(ubicacion)
        db.session.commit()
        return jsonify({'mensaje': 'Ubicación eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ubicaciones/archivo/<archivo_origen>', methods=['GET'])
def get_ubicaciones_by_archivo(archivo_origen):
    """Obtener ubicaciones por archivo de origen"""
    try:
        ubicaciones = Ubicacion.query.filter_by(archivo_origen=archivo_origen).all()
        return jsonify([loc.to_dict() for loc in ubicaciones])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
