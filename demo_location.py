from src.utils.location_utils import get_coordinates, get_timezone, create_location_from_place, local_to_utc, utc_to_local
from datetime import datetime

def demo_location(place_name: str):
    print(f"\nDemostrando funcionalidad para: {place_name}")
    print("-" * 50)

    # 1. Obtener coordenadas
    print("\n1. Obteniendo coordenadas:")
    lat, lon, elevation = get_coordinates(place_name)
    print(f"Latitud: {lat}")
    print(f"Longitud: {lon}")
    print(f"Elevación: {elevation} metros")

    # 2. Obtener zona horaria
    print("\n2. Determinando zona horaria:")
    timezone = get_timezone(lat, lon)
    print(f"Zona horaria: {timezone}")

    # 3. Crear objeto Location
    print("\n3. Creando objeto Location:")
    location = create_location_from_place(place_name)
    print(f"Location creado: {location.name}")
    print(f"Coordenadas: {location.lat}, {location.lon}")
    print(f"Zona horaria: {location.timezone}")

    # 4. Demostrar conversión de tiempo
    print("\n4. Demostrando conversión de tiempo:")
    now = datetime.now()
    print(f"Hora local actual: {now}")
    
    # Convertir a UTC
    utc_time = local_to_utc(now, timezone)
    print(f"En UTC: {utc_time}")
    
    # Convertir de vuelta a hora local
    local_time = utc_to_local(utc_time, timezone)
    print(f"De vuelta a hora local: {local_time}")

if __name__ == "__main__":
    # Probar con algunas ubicaciones
    places = [
        "Buenos Aires, Argentina",
        "Madrid, España",
        "Tokyo, Japan"
    ]
    
    for place in places:
        try:
            demo_location(place)
        except Exception as e:
            print(f"\nError procesando {place}: {str(e)}")
