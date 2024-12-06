"""
Demo de análisis de eclipses y su impacto en una carta natal.
"""
from datetime import datetime
import json
import pytz
from src.calculators.natal_chart import calcular_carta_natal
from src.calculators.eclipse_analysis import analizar_eclipses_periodo
from src.core.constants import EventType

class CustomEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar objetos datetime y EventType."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, EventType):
            return obj.name
        return super().default(obj)

def main():
    # Datos de ejemplo para la carta natal
    datos_usuario = {
        'hora_local': '1990-01-15T14:30:00',
        'lat': -34.6037,
        'lon': -58.3816,
        'zona_horaria': 'America/Argentina/Buenos_Aires',
        'lugar': 'Buenos Aires, Argentina'
    }
    
    try:
        # Calcular carta natal
        print("\n1. Calculando carta natal...")
        carta_natal = calcular_carta_natal(datos_usuario)
        
        # Debug: Mostrar estructura detallada de los puntos
        print("\nEstructura detallada de puntos en la carta natal:")
        for punto, datos in carta_natal['points'].items():
            print(f"\n{punto}:")
            for key, value in datos.items():
                print(f"  {key}: {value}")
        
        # Definir período para análisis de eclipses (año 2024)
        inicio = datetime(2024, 1, 1, tzinfo=pytz.UTC)
        fin = datetime(2024, 12, 31, tzinfo=pytz.UTC)
        
        print(f"\n2. Analizando eclipses para el período {inicio.date()} - {fin.date()}...")
        
        # Analizar eclipses
        resultados = analizar_eclipses_periodo(
            carta_natal,
            inicio,
            fin,
            {
                'latitude': datos_usuario['lat'],
                'longitude': datos_usuario['lon']
            }
        )
        
        # Guardar resultados completos
        output_file = 'analisis_eclipses_2024.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'datos_usuario': datos_usuario,
                'periodo_analisis': {
                    'inicio': inicio.isoformat(),
                    'fin': fin.isoformat()
                },
                'eclipses': resultados
            }, f, indent=2, ensure_ascii=False, cls=CustomEncoder)
        
        print(f"\nSe encontraron {len(resultados)} eclipses en el período.")
        print(f"Resultados detallados guardados en {output_file}")
        
        # Mostrar resumen de los eclipses
        print("\n3. Resumen de eclipses y su impacto astrológico:")
        print("=" * 80)
        
        for eclipse in resultados:
            fecha = datetime.fromisoformat(eclipse['fecha_utc']).strftime('%d/%m/%Y %H:%M UTC')
            tipo = "Solar" if "SOLAR" in str(eclipse['tipo']) else "Lunar"
            signo = eclipse['posicion']['signo']
            grado = eclipse['posicion']['grado']
            casa = eclipse['casa_activada']['numero']
            
            print(f"\nEclipse {tipo} - {fecha}")
            print(f"Posición: {signo} {grado:.2f}° (Casa {casa} en {eclipse['casa_activada']['signo']})")
            
            # Mostrar aspectos significativos
            if eclipse['aspectos']:
                print("\nAspectos importantes:")
                for aspecto in eclipse['aspectos']:
                    print(f"  • {aspecto['tipo'].title()} con {aspecto['planeta']} "
                          f"(orbe: {abs(aspecto['orbe']):.2f}°)")
            
            # Mostrar relación con nodos
            if eclipse['nodos']['conjuncion_nodo']:
                print("\n¡Eclipse cercano a los Nodos Lunares!")
                print(f"  • Distancia al Nodo Norte: {eclipse['nodos']['distancia_nodo_norte']:.1f}°")
                print(f"  • Distancia al Nodo Sur: {eclipse['nodos']['distancia_nodo_sur']:.1f}°")
            
            # Interpretación básica
            print("\nInterpretación:")
            print(f"  • Área de vida afectada: Casa {casa} en {eclipse['casa_activada']['signo']}")
            if eclipse['aspectos']:
                print("  • Planetas activados:")
                for aspecto in eclipse['aspectos']:
                    print(f"    - {aspecto['planeta']} por {aspecto['tipo']}")
            
            print("-" * 80)
            
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print("\nTraceback completo:")
        print(traceback.format_exc())

if __name__ == '__main__':
    main()
