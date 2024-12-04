"""
Script para verificar la precisión del calculador de carta natal usando Immanuel.
"""
from datetime import datetime
import json
from src.calculators.natal_chart import calcular_carta_natal
from src.utils.location_utils import create_location_from_place

def mostrar_carta_natal(carta: dict, titulo: str):
    """Muestra los detalles de una carta natal de forma legible."""
    print(f"\n{titulo}")
    print("=" * len(titulo))
    
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
    for angulo in ['Asc', 'Mc', 'Dsc', 'Ic']:
        if angulo in carta['points']:
            datos = carta['points'][angulo]
            print(f"{angulo:8}: {datos['sign']} {datos['position']}")
    
    # Casas
    print("\nCasas Astrológicas:")
    print("-" * 30)
    for num, datos in carta['houses'].items():
        print(f"Casa {num:2}: {datos['sign']} {datos['position']}")
    
    # Aspectos principales
    if 'aspects' in carta:
        print("\nAspectos Principales:")
        print("-" * 30)
        for aspecto in carta['aspects']:
            print(f"{aspecto['point1']} {aspecto['name']} {aspecto['point2']}")
            print(f"  Orbe: {aspecto['orb']}°")

def test_carta_buenos_aires():
    """
    Prueba el cálculo para Buenos Aires el 1/1/2024 a las 9:00 AM hora local.
    """
    print("\nCalculando carta natal para Buenos Aires")
    print("Fecha: 1 de enero de 2024")
    print("Hora local: 09:00 AM (Argentina)")
    print("-" * 50)

    try:
        # Obtener ubicación
        location = create_location_from_place("Buenos Aires, Argentina")
        
        # Preparar datos
        datos_usuario = {
            "hora_local": "2024-01-01T09:00:00",
            "lat": location.lat,
            "lon": location.lon,
            "zona_horaria": location.timezone,
            "lugar": "Buenos Aires"
        }

        # Calcular carta natal
        carta = calcular_carta_natal(datos_usuario)
        
        # Mostrar resultados
        mostrar_carta_natal(carta, "Carta Natal - Buenos Aires")
        
        # Guardar resultado
        with open("carta_natal_buenos_aires.json", "w", encoding='utf-8') as f:
            json.dump(carta, f, indent=2, ensure_ascii=False)
        print(f"\nResultado completo guardado en: carta_natal_buenos_aires.json")

    except Exception as e:
        print(f"\n❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()

def test_multiples_ubicaciones():
    """
    Prueba el cálculo para diferentes ubicaciones del mundo.
    """
    ubicaciones = [
        "Madrid, España",
        "Tokyo, Japan",
        "New York, USA",
        "Sydney, Australia"
    ]
    
    for lugar in ubicaciones:
        print(f"\nCalculando carta natal para {lugar}")
        print("-" * 50)
        
        try:
            # Obtener ubicación
            location = create_location_from_place(lugar)
            
            # Preparar datos
            datos_usuario = {
                "hora_local": "2024-01-01T12:00:00",
                "lat": location.lat,
                "lon": location.lon,
                "zona_horaria": location.timezone,
                "lugar": lugar
            }
            
            # Calcular carta natal
            carta = calcular_carta_natal(datos_usuario)
            
            # Mostrar resultados
            mostrar_carta_natal(carta, f"Carta Natal - {lugar}")
            
            # Guardar resultado
            filename = f"carta_natal_{lugar.replace(' ', '_').replace(',', '')}.json"
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(carta, f, indent=2, ensure_ascii=False)
            print(f"\nResultado guardado en: {filename}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Verificación del Calculador de Carta Natal")
    print("=========================================")
    
    # Probar con Buenos Aires
    test_carta_buenos_aires()
    
    # Probar con otras ubicaciones
    test_multiples_ubicaciones()
