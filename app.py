from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import folium
from folium import plugins
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///georreferenciacion.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'

# Crear carpetas necesarias
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# ==================== MODELOS ====================

class Usuario(UserMixin, db.Model):
    """Modelo de usuario"""
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    contraseña = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con ubicaciones
    ubicaciones = db.relationship('Ubicacion', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def establecer_contraseña(self, contraseña):
        self.contraseña = generate_password_hash(contraseña)

    def verificar_contraseña(self, contraseña):
        return check_password_hash(self.contraseña, contraseña)

    def __repr__(self):
        return f'<Usuario {self.email}>'


class Ubicacion(db.Model):
    """Modelo de ubicación georeferenciada"""
    __tablename__ = 'ubicaciones'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    archivo_origen = db.Column(db.String(255), nullable=True)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'lat': self.latitud,
            'lon': self.longitud,
            'archivo_origen': self.archivo_origen,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else None
        }

    def __repr__(self):
        return f'<Ubicacion {self.descripcion}>'


# ==================== LOGIN MANAGER ====================

@login_manager.user_loader
def cargar_usuario(id):
    return Usuario.query.get(int(id))


# ==================== UTILIDADES ====================

def allowed_file(filename):
    """Verifica si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_coordinates(coord_string):
    """
    Parsea diferentes formatos de coordenadas:
    - "lat, lon"
    - "lat,lon"
    - "(lat, lon)"
    """
    try:
        coord_string = str(coord_string).strip().replace('(', '').replace(')', '')
        parts = coord_string.split(',')

        if len(parts) == 2:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())

            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon

        return None
    except:
        return None


# ==================== RUTAS PÚBLICAS ====================

@app.route('/')
def index():
    """Redirige al login si no está autenticado, al dashboard si lo está"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de nuevos usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        contraseña = request.form.get('contraseña', '')
        confirmar = request.form.get('confirmar', '')

        # Validaciones
        if not nombre or not email or not contraseña:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('registro'))

        if contraseña != confirmar:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('registro'))

        if len(contraseña) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('registro'))

        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('registro'))

        # Crear nuevo usuario
        usuario = Usuario(nombre=nombre, email=email)
        usuario.establecer_contraseña(contraseña)

        db.session.add(usuario)
        db.session.commit()

        flash('¡Registro exitoso! Por favor inicia sesión', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        contraseña = request.form.get('contraseña', '')

        if not email or not contraseña:
            flash('Email y contraseña son requeridos', 'error')
            return redirect(url_for('login'))

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.verificar_contraseña(contraseña):
            login_user(usuario, remember=request.form.get('recordar'))
            siguiente = request.args.get('next')
            return redirect(siguiente if siguiente else url_for('dashboard'))

        flash('Email o contraseña incorrectos', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))


@app.route('/repair-db')
def repair_db():
    """Reparar base de datos corrupta (solo accesible internamente)"""
    try:
        with app.app_context():
            # Cerrar conexiones existentes
            db.session.remove()
            db.engine.dispose()

            # Eliminar todas las tablas
            db.drop_all()
            # Crear nuevas tablas con schema correcto
            db.create_all()

            # Crear usuario de demo
            usuario_demo = Usuario(
                nombre="Usuario Demo",
                email="demo@test.com"
            )
            usuario_demo.establecer_contraseña("123456")
            db.session.add(usuario_demo)
            db.session.commit()

            # Cerrar sesión nuevamente
            db.session.remove()

            return jsonify({
                'success': True,
                'message': 'Base de datos reparada correctamente',
                'usuario': 'demo@test.com',
                'contraseña': '123456'
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== RUTAS PROTEGIDAS ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal del usuario"""
    return render_template('dashboard.html', usuario=current_user)


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Cargar archivo Excel y guardar coordenadas"""
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('dashboard'))

    file = request.files['file']

    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('dashboard'))

    if not (file and allowed_file(file.filename)):
        flash('Formato de archivo no permitido. Use archivos .xlsx o .xls', 'error')
        return redirect(url_for('dashboard'))

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Leer Excel
        df = pd.read_excel(filepath)

        if len(df.columns) < 2:
            flash('El archivo debe tener al menos 2 columnas', 'error')
            return redirect(url_for('dashboard'))

        # Renombrar columnas
        df.columns = ['descripcion', 'coordenadas'] + list(df.columns[2:])

        # Procesar coordenadas
        locations = []
        errores = 0

        for idx, row in df.iterrows():
            coords = parse_coordinates(row['coordenadas'])
            if coords:
                ubicacion = Ubicacion(
                    descripcion=str(row['descripcion']),
                    latitud=coords[0],
                    longitud=coords[1],
                    archivo_origen=filename,
                    usuario_id=current_user.id
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
            flash('No se encontraron coordenadas válidas', 'error')
            return redirect(url_for('dashboard'))

        db.session.commit()

        # Crear mapa
        map_center = [locations[0]['lat'], locations[0]['lon']]
        mapa = folium.Map(
            location=map_center,
            zoom_start=12,
            tiles='OpenStreetMap'
        )

        for loc in locations:
            folium.Marker(
                location=[loc['lat'], loc['lon']],
                popup=folium.Popup(loc['descripcion'], max_width=300),
                tooltip=loc['descripcion'],
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(mapa)

        plugins.Fullscreen().add_to(mapa)

        map_path = os.path.join('static', f'mapa_{current_user.id}.html')
        mapa.save(map_path)

        if errores > 0:
            flash(f'✅ {len(locations)} ubicaciones guardadas. {errores} coordenadas ignoradas', 'warning')
        else:
            flash(f'✅ {len(locations)} ubicaciones guardadas correctamente', 'success')

        return redirect(url_for('ver_mapa'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el archivo: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


@app.route('/mapa')
@login_required
def ver_mapa():
    """Ver el mapa generado"""
    return render_template('mapa.html', usuario=current_user)


@app.route('/coordenadas')
@login_required
def coordenadas():
    """Ver todas las coordenadas del usuario"""
    ubicaciones = Ubicacion.query.filter_by(usuario_id=current_user.id).all()
    return render_template('coordenadas.html', ubicaciones=ubicaciones, usuario=current_user)


# ==================== API REST ====================

@app.route('/api/ubicaciones', methods=['GET'])
@login_required
def get_ubicaciones():
    """Obtener todas las ubicaciones del usuario autenticado"""
    try:
        ubicaciones = Ubicacion.query.filter_by(usuario_id=current_user.id).all()
        return jsonify([loc.to_dict() for loc in ubicaciones])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ubicaciones/<int:id>', methods=['GET'])
@login_required
def get_ubicacion(id):
    """Obtener una ubicación específica"""
    try:
        ubicacion = Ubicacion.query.get_or_404(id)

        # Verificar que pertenece al usuario actual
        if ubicacion.usuario_id != current_user.id:
            return jsonify({'error': 'No tienes permiso'}), 403

        return jsonify(ubicacion.to_dict())
    except:
        return jsonify({'error': 'Ubicación no encontrada'}), 404


@app.route('/api/ubicaciones', methods=['POST'])
@login_required
def crear_ubicacion():
    """Crear una nueva ubicación manualmente"""
    try:
        data = request.get_json()

        if not data or 'descripcion' not in data or 'latitud' not in data or 'longitud' not in data:
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        lat = float(data['latitud'])
        lon = float(data['longitud'])

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return jsonify({'error': 'Coordenadas fuera de rango'}), 400

        ubicacion = Ubicacion(
            descripcion=str(data['descripcion']),
            latitud=lat,
            longitud=lon,
            archivo_origen=data.get('archivo_origen', 'Manual'),
            usuario_id=current_user.id
        )

        db.session.add(ubicacion)
        db.session.commit()

        return jsonify(ubicacion.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/ubicaciones/<int:id>', methods=['PUT'])
@login_required
def actualizar_ubicacion(id):
    """Actualizar una ubicación"""
    try:
        ubicacion = Ubicacion.query.get_or_404(id)

        if ubicacion.usuario_id != current_user.id:
            return jsonify({'error': 'No tienes permiso'}), 403

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
@login_required
def eliminar_ubicacion(id):
    """Eliminar una ubicación"""
    try:
        ubicacion = Ubicacion.query.get_or_404(id)

        if ubicacion.usuario_id != current_user.id:
            return jsonify({'error': 'No tienes permiso'}), 403

        db.session.delete(ubicacion)
        db.session.commit()
        return jsonify({'mensaje': 'Ubicación eliminada'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== CREAR TABLAS ====================

def init_db():
    """Inicializar base de datos con auto-reparación"""
    with app.app_context():
        try:
            # Intentar crear todas las tablas
            db.create_all()

            # Verificar que la tabla ubicaciones tiene la columna usuario_id
            inspector = db.inspect(db.engine)
            if 'ubicaciones' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('ubicaciones')]
                if 'usuario_id' not in columns:
                    print("[!] Columna usuario_id faltante en ubicaciones. Reparando...")
                    db.drop_all()
                    db.create_all()
                    print("[+] Base de datos reparada")
        except Exception as e:
            print(f"[!] Error al inicializar BD: {str(e)}")
            print("[*] Intentando reparación completa...")
            try:
                db.drop_all()
                db.create_all()
                print("[+] Base de datos reparada exitosamente")
            except Exception as repair_error:
                print(f"[!] Error en reparación: {str(repair_error)}")

# Inicializar BD al iniciar la app
init_db()


if __name__ == '__main__':
    # En producción (Render), gunicorn ejecutará la app
    # En desarrollo local, ejecutar con debug=True
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
