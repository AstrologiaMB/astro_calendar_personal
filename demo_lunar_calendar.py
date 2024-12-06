"""
Demo para probar el cálculo de eventos lunares con casas natales.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from src.calculators.lunar_calendar import LunarCalendarCalculator
import json
import traceback

def main():
    try:
        print("Iniciando cálculo de eventos lunares...")
        
        # Datos de ejemplo (Buenos Aires)
        datos_natal = {
            'hora_local': '2000-01-01T12:00:00',  # Fecha natal de ejemplo
            'lat': -34.6037,
            'lon': -58.3816,
            'zona_horaria': 'America/Argentina/Buenos_Aires',
            'lugar': 'Buenos Aires, Argentina'
        }
        
        print("Creando calculador...")
        calc = LunarCalendarCalculator(datos_natal)
        
        print("Configurando fechas...")
        inicio = datetime(2024, 1, 1, tzinfo=ZoneInfo('UTC'))
        fin = datetime(2024, 12, 31, tzinfo=ZoneInfo('UTC'))
        
        print("Calculando eventos lunares...")
        eventos = calc.calcular_eventos_lunares(inicio, fin)
        
        print(f"Se encontraron {len(eventos)} eventos lunares")
        
        # Guardar resultados
        output = {
            'datos_natal': datos_natal,
            'eventos': eventos
        }
        
        print("Guardando resultados en JSON...")
        with open('eventos_lunares_2024.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, default=str)
            
        # Mostrar algunos eventos de ejemplo
        print("\nEjemplos de eventos lunares calculados:")
        for evento in eventos[:4]:  # Mostrar primeros 4 eventos
            print(f"\n{evento['tipo']} - {evento['fecha_utc']}")
            print(f"Posición: {evento['signo']} {evento['grado']:.2f}°")
            print(f"Casa: {evento['casa']}")
            print(f"Descripción: {evento['descripcion']}")
            
    except Exception as e:
        print(f"\nError durante la ejecución:")
        print(traceback.format_exc())

if __name__ == '__main__':
    main()
