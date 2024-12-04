"""
Demostración de la integración entre el Módulo 1 (Ingreso de Datos) y
el Módulo 2 (Cálculo de Carta Natal).
"""
from datetime import datetime
import json
from src.utils.location_utils import create_location_from_place
from src.calculators.natal_chart import calcular_carta_natal

def solicitar_datos_usuario():
    """
    Módulo 1: Solicita y valida los datos del usuario.
    
    Returns:
        Dict con los datos validados
    """
    print("\nMódulo 1: Ingreso de Datos del Usuario")
    print("=" * 40)
    
    try:
        # 1. Solicitar lugar de nacimiento
        print("\nIngrese el lugar de nacimiento")
        print("Ejemplo: 'Buenos Aires, Argentina' o 'Madrid, España'")
        lugar = input("Lugar: ").strip()
        
        # 2. Obtener datos de ubicación
        print("\nBuscando coordenadas y zona horaria...")
        location = create_location_from_place(lugar)
        
        print(f"Ubicación encontrada:")
        print(f"  Latitud: {location.lat}")
        print(f"  Longitud: {location.lon}")
        print(f"  Zona Horaria: {location.timezone}")
        
        # 3. Solicitar fecha y hora
        print("\nIngrese la fecha de nacimiento")
        fecha = input("Fecha (YYYY-MM-DD): ").strip()
        hora = input("Hora local (HH:MM): ").strip()
        
        # 4. Construir fecha/hora completa
        fecha_hora = f"{fecha}T{hora}:00"
        
        # 5. Preparar datos para el cálculo
        datos_usuario = {
            "hora_local": fecha_hora,
            "lat": location.lat,
            "lon": location.lon,
            "zona_horaria": location.timezone,
            "lugar": lugar
        }
        
        return datos_usuario
        
    except Exception as e:
        print(f"\n❌ Error en el ingreso de datos: {str(e)}")
        raise

def mostrar_carta_natal(carta: dict):
    """
    Muestra los resultados de la carta natal de forma legible.
    """
    print("\nResultados de la Carta Natal")
    print("=" * 40)
    
    # Información de ubicación
    print("\nInformación de Ubicación:")
    print("-" * 30)
    print(f"Lugar: {carta['location']['name']}")
    print(f"Latitud: {carta['location']['latitude']}")
    print(f"Longitud: {carta['location']['longitude']}")
    print(f"Zona Horaria: {carta['location']['timezone']}")
    
    # Posiciones planetarias
    print("\nPosiciones Planetarias:")
    print("-" * 30)
    for planeta, datos in carta['points'].items():
        if planeta in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                      'Saturn', 'Uranus', 'Neptune', 'Pluto']:
            print(f"{planeta:8}: {datos['sign']} {datos['position']}")
            if datos.get('retrograde'):
                print("         (Retrógrado)")
    
    # Ángulos principales
    print("\nÁngulos Principales:")
    print("-" * 30)
    for angulo in ['Asc', 'Mc']:
        if angulo in carta['points']:
            datos = carta['points'][angulo]
            print(f"{angulo:8}: {datos['sign']} {datos['position']}")
    
    # Casas
    print("\nCasas Astrológicas:")
    print("-" * 30)
    for num, datos in carta['houses'].items():
        print(f"Casa {num:2}: {datos['sign']} {datos['position']}")

def main():
    """Función principal que integra los módulos."""
    print("Demostración del Sistema de Carta Natal")
    print("======================================")
    
    try:
        # Módulo 1: Solicitar datos
        datos_usuario = solicitar_datos_usuario()
        
        print("\nMódulo 2: Cálculo de Carta Natal")
        print("=" * 40)
        
        # Módulo 2: Calcular carta natal
        carta = calcular_carta_natal(datos_usuario)
        
        # Mostrar resultados
        mostrar_carta_natal(carta)
        
        # Guardar resultado
        filename = f"carta_natal_{datos_usuario['lugar'].replace(' ', '_').replace(',', '')}.json"
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(carta, f, indent=2, ensure_ascii=False)
        print(f"\nResultado completo guardado en: {filename}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
