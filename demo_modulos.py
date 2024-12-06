"""
Demo completa de todos los módulos del Calendario Astrológico Personalizado.
"""
from datetime import datetime
import json
import pytz
from src.calculators.natal_chart import calcular_carta_natal
from src.calculators.eclipse_analysis import analizar_eclipses_periodo
from src.calculators.lunar_calendar import LunarCalendarCalculator
from src.core.constants import EventType
from src.utils.location_utils import get_coordinates, get_timezone

# Mapeo de signos en inglés a español
SIGNOS = {
    'Aries': 'Aries',
    'Taurus': 'Tauro',
    'Gemini': 'Géminis',
    'Cancer': 'Cáncer',
    'Leo': 'Leo',
    'Virgo': 'Virgo',
    'Libra': 'Libra',
    'Scorpio': 'Escorpio',
    'Sagittarius': 'Sagitario',
    'Capricorn': 'Capricornio',
    'Aquarius': 'Acuario',
    'Pisces': 'Piscis'
}

def traducir_signo(signo: str) -> str:
    """Traduce el nombre del signo de inglés a español."""
    return SIGNOS.get(signo, signo)

def guardar_json(datos: dict, archivo: str):
    """Guarda datos en formato JSON."""
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, EventType):
                return obj.name
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return super().default(obj)
    
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False, cls=CustomEncoder)

def solicitar_input(prompt: str, validar=None, ejemplo: str = None) -> str:
    """Solicita input al usuario con validación."""
    while True:
        if ejemplo:
            print(f"\n{prompt}")
            print(f"Ejemplo: {ejemplo}")
        else:
            print(f"\n{prompt}")
            
        valor = input("> ").strip()
        
        if not valor:
            print("Error: El valor no puede estar vacío.")
            continue
            
        if validar:
            try:
                return validar(valor)
            except ValueError as e:
                print(f"Error: {str(e)}")
                continue
        return valor

def validar_fecha(fecha: str) -> str:
    """Valida y formatea una fecha."""
    try:
        dia, mes, anio = map(int, fecha.split('/'))
        if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1900 <= anio <= 2100):
            raise ValueError("Fecha fuera de rango válido")
        return f"{anio:04d}-{mes:02d}-{dia:02d}"
    except:
        raise ValueError("Formato de fecha inválido (debe ser DD/MM/AAAA)")

def validar_hora(hora: str) -> str:
    """Valida y formatea una hora."""
    try:
        hh, mm = map(int, hora.split(':'))
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError("Hora fuera de rango válido")
        return f"{hh:02d}:{mm:02d}"
    except:
        raise ValueError("Formato de hora inválido (debe ser HH:MM)")

def solicitar_datos_usuario():
    """Solicita los datos del usuario de forma interactiva."""
    print("\nINGRESO DE DATOS NATALES")
    print("=" * 50)
    print("Por favor, ingrese sus datos de nacimiento con cuidado.")
    print("Esta información es crucial para los cálculos astrológicos.")
    print("-" * 50)
    
    # Fecha y hora de nacimiento
    fecha = solicitar_input(
        "Fecha de nacimiento (DD/MM/AAAA)",
        validar_fecha,
        "26/12/1964"
    )
    
    hora = solicitar_input(
        "Hora de nacimiento (HH:MM)",
        validar_hora,
        "21:12"
    )
    
    # Crear timestamp
    hora_local = f"{fecha}T{hora}:00"
    
    # Lugar de nacimiento
    print("\nLUGAR DE NACIMIENTO")
    print("-" * 50)
    print("Ingrese el lugar de nacimiento (ciudad, país)")
    print("Ejemplos: Buenos Aires, Argentina")
    print("         Madrid, España")
    print("         New York, USA")
    
    lugar = solicitar_input(
        "Lugar de nacimiento",
        ejemplo="Buenos Aires, Argentina"
    )
    
    print("\nBuscando coordenadas y zona horaria...")
    try:
        # Obtener coordenadas
        lat, lon, _ = get_coordinates(lugar)
        zona_horaria = get_timezone(lat, lon)
        
        print("\nDatos obtenidos:")
        print(f"  • Latitud: {lat:.4f}° {'Sur' if lat < 0 else 'Norte'}")
        print(f"  • Longitud: {lon:.4f}° {'Oeste' if lon < 0 else 'Este'}")
        print(f"  • Zona Horaria: {zona_horaria}")
        
    except Exception as e:
        print(f"\nError al obtener datos del lugar: {str(e)}")
        print("Por favor, ingrese los datos manualmente:")
        
        lat = float(solicitar_input(
            "Latitud (decimal, ej: -34.6037 para sur)",
            lambda x: float(x)
        ))
        
        lon = float(solicitar_input(
            "Longitud (decimal, ej: -58.3816 para oeste)",
            lambda x: float(x)
        ))
        
        print("\nZonas horarias comunes:")
        print("  • America/Argentina/Buenos_Aires")
        print("  • America/New_York")
        print("  • Europe/Madrid")
        print("  • Asia/Tokyo")
        
        zona_horaria = solicitar_input(
            "Zona horaria",
            lambda x: str(pytz.timezone(x))
        )
    
    datos = {
        'hora_local': hora_local,
        'lat': lat,
        'lon': lon,
        'zona_horaria': zona_horaria,
        'lugar': lugar
    }
    
    # Mostrar resumen de datos
    print("\nRESUMEN DE DATOS NATALES")
    print("=" * 50)
    print(f"Fecha y Hora: {datetime.fromisoformat(hora_local).strftime('%d/%m/%Y %H:%M')}")
    print(f"Lugar: {lugar}")
    print(f"Coordenadas: {abs(lat):.4f}°{'S' if lat < 0 else 'N'}, "
          f"{abs(lon):.4f}°{'W' if lon < 0 else 'E'}")
    print(f"Zona Horaria: {zona_horaria}")
    print("-" * 50)
    
    return datos

def main():
    try:
        print("\n=== DEMO COMPLETA DEL CALENDARIO ASTROLÓGICO PERSONALIZADO ===")
        print("=" * 70)
        
        # Solicitar datos del usuario
        datos_usuario = solicitar_datos_usuario()
        
        # MÓDULO 1: Eventos Lunares
        print("\n1. MÓDULO DE EVENTOS LUNARES")
        print("-" * 70)
        
        inicio = datetime(2024, 1, 1, tzinfo=pytz.UTC)
        fin = datetime(2024, 12, 31, tzinfo=pytz.UTC)
        
        print(f"\nCalculando eventos lunares para el período {inicio.date()} - {fin.date()}...")
        
        # Crear calculador lunar
        lunar_calc = LunarCalendarCalculator(datos_usuario)
        eventos_lunares = lunar_calc.calcular_eventos_lunares(inicio, fin)
        
        # Guardar eventos lunares
        archivo_lunar = 'eventos_lunares_2024.json'
        guardar_json(eventos_lunares, archivo_lunar)
        print(f"Eventos lunares guardados en {archivo_lunar}")
        
        # Mostrar resumen de eventos lunares
        total_eventos = len(eventos_lunares)
        tipos_eventos = {}
        for evento in eventos_lunares:
            tipo = str(evento['tipo'])
            tipos_eventos[tipo] = tipos_eventos.get(tipo, 0) + 1
        
        print("\nResumen de eventos lunares encontrados:")
        for tipo, cantidad in tipos_eventos.items():
            print(f"  • {tipo}: {cantidad} eventos")
        
        # MÓDULO 2: Carta Natal
        print("\n2. MÓDULO DE CARTA NATAL")
        print("-" * 70)
        
        print("\nCalculando carta natal...")
        carta_natal = calcular_carta_natal(datos_usuario)
        
        # Guardar carta natal
        archivo_natal = 'carta_natal.json'
        guardar_json(carta_natal, archivo_natal)
        print(f"Carta natal guardada en {archivo_natal}")
        
        # Mostrar resumen de la carta natal
        print("\nResumen de la carta natal:")
        print(f"  • Ascendente: {traducir_signo(carta_natal['points']['Asc']['sign'])} {carta_natal['points']['Asc']['position']}")
        print(f"  • Sol en: {traducir_signo(carta_natal['points']['Sun']['sign'])} {carta_natal['points']['Sun']['position']}")
        print(f"  • Luna en: {traducir_signo(carta_natal['points']['Moon']['sign'])} {carta_natal['points']['Moon']['position']}")
        print(f"  • Nodo Norte en: {traducir_signo(carta_natal['points']['North Node']['sign'])} {carta_natal['points']['North Node']['position']}")
        
        # MÓDULO 3: Análisis de Eclipses y Fases Lunares
        print("\n3. MÓDULO DE ANÁLISIS DE ECLIPSES Y FASES LUNARES")
        print("-" * 70)
        
        print(f"\nAnalizando eclipses para el período {inicio.date()} - {fin.date()}...")
        resultados_eclipses = analizar_eclipses_periodo(
            carta_natal,
            inicio,
            fin,
            {
                'latitude': datos_usuario['lat'],
                'longitude': datos_usuario['lon']
            }
        )
        
        # Guardar análisis de eclipses
        archivo_eclipses = 'analisis_eclipses_2024.json'
        guardar_json({
            'datos_usuario': datos_usuario,
            'periodo_analisis': {
                'inicio': inicio.isoformat(),
                'fin': fin.isoformat()
            },
            'eclipses': resultados_eclipses
        }, archivo_eclipses)
        print(f"Análisis de eclipses guardado en {archivo_eclipses}")
        
        # Mostrar resumen de eclipses y fases lunares
        print(f"\nSe encontraron {len(resultados_eclipses)} eclipses en el período:")
        for eclipse in resultados_eclipses:
            fecha = datetime.fromisoformat(eclipse['fecha_utc']).strftime('%d/%m/%Y %H:%M UTC')
            tipo = "Solar" if "SOLAR" in str(eclipse['tipo']) else "Lunar"
            signo = traducir_signo(eclipse['posicion']['signo'])
            grado = eclipse['posicion']['grado']
            casa = eclipse['casa_activada']['numero']
            casa_signo = traducir_signo(eclipse['casa_activada']['signo'])
            
            print(f"\nEclipse {tipo} - {fecha}")
            print(f"  • Posición: {signo} {grado:.2f}° (Casa {casa} en {casa_signo})")
            
            if eclipse['aspectos']:
                print("  • Aspectos importantes:")
                for aspecto in eclipse['aspectos']:
                    print(f"    - {aspecto['tipo'].title()} con {aspecto['planeta']} "
                          f"(orbe: {abs(aspecto['orbe']):.2f}°)")
        
        # Mostrar fases lunares
        print("\nFases Lunares Principales:")
        print("-" * 70)
        
        # Agrupar eventos por tipo
        lunas_nuevas = []
        lunas_llenas = []
        
        for evento in eventos_lunares:
            fecha = datetime.fromisoformat(str(evento['fecha_utc'])).strftime('%d/%m/%Y %H:%M UTC')
            signo = traducir_signo(evento['signo'])
            info = {
                'fecha': fecha,
                'signo': signo,
                'grado': evento['grado'],
                'casa': evento['casa']
            }
            
            if "NUEVA" in str(evento['tipo']):
                lunas_nuevas.append(info)
            else:
                lunas_llenas.append(info)
        
        print("\nLunas Nuevas:")
        for luna in lunas_nuevas:
            print(f"  • {luna['fecha']}")
            print(f"    {luna['signo']} {luna['grado']:.2f}° (Casa {luna['casa']})")
        
        print("\nLunas Llenas:")
        for luna in lunas_llenas:
            print(f"  • {luna['fecha']}")
            print(f"    {luna['signo']} {luna['grado']:.2f}° (Casa {luna['casa']})")
        
        print("\n=== DEMO COMPLETADA EXITOSAMENTE ===")
        print("Se han generado tres archivos JSON con todos los resultados:")
        print(f"1. {archivo_lunar} - Eventos lunares del período")
        print(f"2. {archivo_natal} - Carta natal del usuario")
        print(f"3. {archivo_eclipses} - Análisis de eclipses personalizado")
            
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print("\nTraceback completo:")
        print(traceback.format_exc())

if __name__ == '__main__':
    main()
