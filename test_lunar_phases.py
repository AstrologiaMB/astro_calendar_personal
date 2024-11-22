from datetime import datetime
import pytz
from src.core.location import Location
from src.calculators.lunar_phases import LunarPhaseCalculator

def test_lunar_phases():
    # Crear ubicación de prueba (Buenos Aires)
    location = Location(
        lat=-34.60,
        lon=-58.45,
        name="Buenos_Aires",
        timezone="America/Argentina/Buenos_Aires",
        elevation=25
    )
    
    # Crear observador
    observer = location.create_ephem_observer()
    
    # Crear calculador
    calculator = LunarPhaseCalculator(observer)
    
    # Definir período de prueba (un mes)
    start_date = datetime(2025, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime(2025, 2, 1, tzinfo=pytz.UTC)
    
    # Calcular eventos
    events = calculator.calculate_phases(start_date, end_date)
    
    # Mostrar resultados
    print(f"\nEventos lunares encontrados entre {start_date.date()} y {end_date.date()}:")
    for event in sorted(events, key=lambda x: x.fecha_utc):
        print(f"\nFecha UTC: {event.fecha_utc}")
        print(f"Fecha Local: {event.fecha_local}")
        print(f"Tipo: {event.tipo_evento.value}")
        print(f"Descripción: {event.descripcion}")
        if event.elevacion is not None:
            print(f"Elevación: {event.elevacion:.1f}°")
            print(f"Azimut: {event.azimut:.1f}°")

if __name__ == "__main__":
    try:
        test_lunar_phases()
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()