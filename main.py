import os
import swisseph as swe
from datetime import datetime
import pytz
from src.core.location import Location
from src.calculators.lunar_phases import LunarPhaseCalculator
from src.calculators.eclipses import EclipseCalculator
from src.calculators.ingresses import IngressCalculator
from src.calculators.retrogrades import RetrogradeCalculator
from src.calculators.aspects import AspectCalculator
from src.calculators.nodes import NodeCalculator
from src.output.csv_writer import CSVWriter

class AstronomicalCalendar:
    def __init__(self, year: int):
        self.year = year
        self.location = Location(
            lat=-34.60,
            lon=-58.45,
            name="Buenos_Aires",
            timezone="America/Argentina/Buenos_Aires",
            elevation=25
        )
        self.events = []

        # Inicializar Swiss Ephemeris
        ephe_path = os.path.expanduser("~/.local/share/ephe")
        swe.set_ephe_path(ephe_path)

        # Inicializar calculadores
        observer = self.location.create_ephem_observer()
        self.lunar_calculator = LunarPhaseCalculator(observer)
        self.eclipse_calculator = EclipseCalculator(observer)
        self.ingress_calculator = IngressCalculator()
        self.retrograde_calculator = RetrogradeCalculator()
        self.aspect_calculator = AspectCalculator()
        self.node_calculator = NodeCalculator()

    def calculate_all_events(self):
        """Calcula todos los eventos del año"""
        print(f"Calculando eventos astronómicos para {self.year}...")
        
        start_date = datetime(self.year, 1, 1, tzinfo=pytz.UTC)
        end_date = datetime(self.year + 1, 1, 1, tzinfo=pytz.UTC)

        # Calcular eventos
        print("Calculando fases lunares...")
        self.events.extend(self.lunar_calculator.calculate_phases(start_date, end_date))
        
        print("Calculando eclipses...")
        self.events.extend(self.eclipse_calculator.calculate_eclipses(start_date, end_date))
        
        print("Calculando ingresos a signos...")
        self.events.extend(self.ingress_calculator.calculate_ingresses(start_date, end_date))
        
        print("Calculando retrogradaciones...")
        self.events.extend(self.retrograde_calculator.calculate_retrogrades(start_date, end_date))
        
        print("Calculando aspectos planetarios...")
        self.events.extend(self.aspect_calculator.calculate_aspects(start_date, end_date))
        
        print("Calculando movimientos nodales...")
        self.events.extend(self.node_calculator.calculate_node_ingresses(start_date, end_date))

        # Ordenar eventos por fecha
        self.events.sort(key=lambda x: x.fecha_utc)
        
        print(f"Se encontraron {len(self.events)} eventos.")

    def save_to_csv(self, filename: str = None) -> str:
        """Guarda los eventos en un archivo CSV"""
        if filename is None:
            filename = f'eventos_astronomicos_{self.year}_BuenosAires.csv'
            
        CSVWriter.write_events(self.events, filename)
        return filename


def main():
    try:
        # Solicitar año
        year = int(input("Ingresa el año para el calendario (ejemplo: 2025): "))
        if not 1900 <= year <= 2100:
            raise ValueError("El año debe estar entre 1900 y 2100")

        # Crear calendario y calcular eventos
        calendar = AstronomicalCalendar(year)
        calendar.calculate_all_events()

        # Guardar resultados
        filename = calendar.save_to_csv()

        # Mostrar resultados
        print(f"\nSe ha generado el archivo {filename} con los siguientes eventos:")
        print(f"Ubicación: Buenos Aires (-34.60° -58.45°)")
        print(f"Zona horaria: America/Argentina/Buenos_Aires\n")

        for event in calendar.events:
            print(f"{event.fecha_local.strftime('%d/%m/%Y %H:%M')} "
                  f"({event.tipo_evento.value})")
            print(f"{event.descripcion}")
            if event.elevacion is not None:
                print(f"Elevación: {event.elevacion:.1f}°, "
                      f"Azimut: {event.azimut:.1f}°")
            print()

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
# Esto es una prueba en astro_calendar_personal