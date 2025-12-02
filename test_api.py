#!/usr/bin/env python
"""
Script de prueba para la API REST del Sistema de Georreferenciación
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api/ubicaciones"

def print_separator():
    print("\n" + "="*60 + "\n")

def test_get_all():
    """Prueba: Obtener todas las ubicaciones"""
    print("1️⃣  PRUEBA: Obtener todas las ubicaciones")
    print("-" * 60)
    try:
        response = requests.get(BASE_URL)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Cantidad de ubicaciones: {len(data)}")
        if data:
            print("\nPrimeras ubicaciones:")
            for ubicacion in data[:3]:
                print(f"  - {ubicacion['descripcion']} ({ubicacion['lat']}, {ubicacion['lon']})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_create():
    """Prueba: Crear una nueva ubicación"""
    print("\n2️⃣  PRUEBA: Crear una nueva ubicación")
    print("-" * 60)
    try:
        nueva_ubicacion = {
            "descripcion": "Lugar de Prueba - " + datetime.now().strftime("%H:%M:%S"),
            "latitud": -12.0462,
            "longitud": -77.0371,
            "archivo_origen": "test_api.py"
        }
        print(f"Datos enviados: {json.dumps(nueva_ubicacion, indent=2)}")

        response = requests.post(BASE_URL, json=nueva_ubicacion)
        print(f"\nStatus Code: {response.status_code}")
        data = response.json()
        print(f"Ubicación creada: {data['descripcion']} (ID: {data['id']})")
        return response.status_code == 201, data.get('id') if response.status_code == 201 else None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None

def test_get_by_id(location_id):
    """Prueba: Obtener una ubicación por ID"""
    print(f"\n3️⃣  PRUEBA: Obtener ubicación por ID ({location_id})")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/{location_id}")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Ubicación encontrada: {data['descripcion']}")
        print(f"Coordenadas: {data['lat']}, {data['lon']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_update(location_id):
    """Prueba: Actualizar una ubicación"""
    print(f"\n4️⃣  PRUEBA: Actualizar ubicación (ID: {location_id})")
    print("-" * 60)
    try:
        datos_actualizados = {
            "descripcion": "Lugar Actualizado - " + datetime.now().strftime("%H:%M:%S"),
            "latitud": -12.0500,
            "longitud": -77.0400
        }
        print(f"Datos a actualizar: {json.dumps(datos_actualizados, indent=2)}")

        response = requests.put(f"{BASE_URL}/{location_id}", json=datos_actualizados)
        print(f"\nStatus Code: {response.status_code}")
        data = response.json()
        print(f"Ubicación actualizada: {data['descripcion']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_delete(location_id):
    """Prueba: Eliminar una ubicación"""
    print(f"\n5️⃣  PRUEBA: Eliminar ubicación (ID: {location_id})")
    print("-" * 60)
    try:
        response = requests.delete(f"{BASE_URL}/{location_id}")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Resultado: {data['mensaje']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + "  PRUEBAS DE API - SISTEMA DE GEORREFERENCIACIÓN  ".center(58) + "║")
    print("╚" + "="*58 + "╝")

    print(f"\n📍 URL Base: {BASE_URL}")

    try:
        # Prueba de conexión
        print("\n🔌 Verificando conexión con el servidor...")
        response = requests.get("http://localhost:5000/", timeout=2)
        print("✅ Servidor conectado")
    except:
        print("❌ No se puede conectar con el servidor")
        print("   Asegúrate de que la aplicación está corriendo: python app.py")
        return

    results = []

    # Pruebas
    results.append(("Obtener todas", test_get_all()))
    print_separator()

    crear_ok, location_id = test_create()
    results.append(("Crear ubicación", crear_ok))
    print_separator()

    if location_id:
        results.append(("Obtener por ID", test_get_by_id(location_id)))
        print_separator()

        results.append(("Actualizar", test_update(location_id)))
        print_separator()

        results.append(("Eliminar", test_delete(location_id)))
        print_separator()

    # Resumen
    print("\n📊 RESUMEN DE PRUEBAS")
    print("="*60)
    for nombre, resultado in results:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{nombre:.<40} {estado}")

    total_ok = sum(1 for _, r in results if r)
    print("="*60)
    print(f"Total: {total_ok}/{len(results)} pruebas exitosas")

    if total_ok == len(results):
        print("\n🎉 ¡Todas las pruebas pasaron!")
    else:
        print(f"\n⚠️  {len(results) - total_ok} prueba(s) fallaron")

if __name__ == "__main__":
    main()
