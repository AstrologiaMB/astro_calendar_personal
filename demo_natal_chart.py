from datetime import datetime
import json
from src.utils.location_utils import create_location_from_place
from src.calculators.natal_chart import calcular_carta_natal

def format_position(position):
    """Formatea una posición planetaria para mostrarla de forma legible."""
    return f"{position['sign']} {position['degrees_in_sign']:.2f}° (Long: {position['longitude']:.2f}°)"

def demo_carta_natal(lugar: str, fecha_hora_utc: str):
    """
    Demuestra el cálculo de una carta natal para un lugar y tiempo específicos.
    
    Args:
        lugar: Nombre del lugar de nacimiento
        fecha_hora_utc: Fecha y hora en UTC (formato ISO)
    """
    print(f"\nCalculando carta natal para:")
    print(f"Lugar: {lugar}")
    print(f"Fecha/Hora (UTC): {fecha_hora_utc}")
    print("-" * 50)

    try:
        # Obtener datos de ubicación
        location = create_location_from_place(lugar)
        print(f"\nUbicación encontrada:")
        print(f"Latitud: {location.lat}")
        print(f"Longitud: {location.lon}")
        print(f"Zona Horaria: {location.timezone}")

        # Preparar datos para el cálculo
        datos_usuario = {
            "hora_utc": fecha_hora_utc,
            "lat": location.lat,
            "lon": location.lon,
            "zona_horaria": location.timezone,
            "lugar": lugar
        }

        # Calcular carta natal
        carta = calcular_carta_natal(datos_usuario)

        # Mostrar resultados
        print("\nPosiciones Planetarias:")
        print("-" * 30)
        for planeta, datos in carta['planets'].items():
            print(f"{planeta:8}: {format_position(datos)}")

        print("\nÁngulos Principales:")
        print("-" * 30)
        for angulo, datos in carta['angles'].items():
            print(f"{angulo:8}: {datos['longitude']:.2f}° - {datos['label']}")

        print("\nCasas Astrológicas:")
        print("-" * 30)
        for num, datos in carta['houses'].items():
            print(f"Casa {num:2}: {datos['start']:.2f}° a {datos['end']:.2f}°")

        # Guardar resultado en archivo JSON
        output_file = f"carta_natal_{lugar.replace(' ', '_')}_{fecha_hora_utc.split('T')[0]}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(carta, f, indent=2, ensure_ascii=False)
        print(f"\nResultado completo guardado en: {output_file}")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    # Ejemplo 1: Buenos Aires, 1 de enero de 2000 al mediodía UTC
    demo_carta_natal(
        "Buenos Aires, Argentina",
        "2000-01-01T12:00:00"
    )

    # Ejemplo 2: Madrid, 15 de julio de 1985 a las 15:30 UTC
    demo_carta_natal(
        "Madrid, España",
        "1985-07-15T15:30:00"
    )

    # Ejemplo 3: Tokyo, 21 de diciembre de 1990 a las 22:15 UTC
    demo_carta_natal(
        "Tokyo, Japan",
        "1990-12-21T22:15:00"
    )
