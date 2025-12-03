#!/usr/bin/env python
"""
Script para recrear la base de datos con la estructura correcta
"""

from app import app, db, Usuario, Ubicacion

print("🔄 Recreando base de datos...")

with app.app_context():
    # Eliminar todas las tablas
    db.drop_all()
    print("✅ Tablas antiguas eliminadas")

    # Crear todas las tablas nuevas
    db.create_all()
    print("✅ Tablas nuevas creadas")

    # Crear usuario de demo para pruebas
    usuario_demo = Usuario(
        nombre="Usuario Demo",
        email="demo@test.com"
    )
    usuario_demo.establecer_contraseña("123456")

    db.session.add(usuario_demo)
    db.session.commit()

    print("✅ Usuario de demo creado:")
    print("   Email: demo@test.com")
    print("   Contraseña: 123456")
    print("\n🎉 Base de datos lista para usar")
