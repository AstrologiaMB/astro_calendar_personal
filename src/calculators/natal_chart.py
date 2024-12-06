"""
Módulo para el cálculo de cartas natales usando nuestra implementación local de Immanuel.
"""
from datetime import datetime
from typing import Dict, Any
from zoneinfo import ZoneInfo
import swisseph as swe
from ..core.location import Location
from ..immanuel import Subject, Natal
from ..utils.time_utils import julian_day

def local_to_utc(local_time: datetime, timezone: str) -> datetime:
    """Convierte hora local a UTC."""
    local_tz = ZoneInfo(timezone)
    if local_time.tzinfo is None:
        local_time = local_time.replace(tzinfo=local_tz)
    return local_time.astimezone(ZoneInfo('UTC'))

def format_coords(lat: float, lon: float) -> tuple[str, str]:
    """
    Convierte coordenadas decimales al formato requerido.
    
    Args:
        lat: Latitud decimal
        lon: Longitud decimal
        
    Returns:
        Tuple con (latitud, longitud) en formato 'DD.DDn/s' y 'DD.DDe/w'
    """
    lat_str = f"{abs(lat):.4f}{'s' if lat < 0 else 'n'}"
    lon_str = f"{abs(lon):.4f}{'w' if lon < 0 else 'e'}"
    return lat_str, lon_str

def get_zodiac_sign(longitude: float) -> str:
    """Obtiene el signo zodiacal para una longitud dada."""
    signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    sign_num = int(longitude / 30)
    return signs[sign_num]

def format_position(longitude: float) -> str:
    """Formatea una posición zodiacal en grados y minutos."""
    total_degrees = longitude % 30
    degrees = int(total_degrees)
    minutes = int((total_degrees - degrees) * 60)
    return f"{degrees}°{minutes:02d}'"

def calcular_carta_natal(datos_usuario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función principal para calcular una carta natal.
    
    Args:
        datos_usuario: Diccionario con los datos del usuario:
            - hora_local: str (formato ISO)
            - lat: float
            - lon: float
            - zona_horaria: str
            
    Returns:
        Dict con la carta natal calculada
    """
    try:
        # Convertir hora local a UTC
        local_time = datetime.fromisoformat(datos_usuario['hora_local'].replace('Z', '+00:00'))
        utc_time = local_to_utc(local_time, datos_usuario['zona_horaria'])
        
        # Convertir coordenadas al formato requerido
        lat_str, lon_str = format_coords(datos_usuario['lat'], datos_usuario['lon'])
        
        # Crear sujeto para la carta natal
        native = Subject(
            date_time=utc_time.strftime('%Y-%m-%d %H:%M'),
            latitude=lat_str,
            longitude=lon_str
        )
        
        # Calcular carta natal
        natal_chart = Natal(native)
        
        # Obtener resultado como diccionario
        result = natal_chart.to_dict()
        
        # Calcular nodos lunares usando Swiss Ephemeris
        jd = julian_day(utc_time)
        
        # Nodo Norte
        node_data = swe.calc_ut(jd, swe.TRUE_NODE)[0]
        node_lon = node_data[0]
        
        # Agregar nodos a los puntos
        result['points']['North Node'] = {
            'longitude': node_lon,
            'latitude': 0.0,
            'distance': 0.0,
            'speed': 0.0,
            'sign': get_zodiac_sign(node_lon),
            'position': format_position(node_lon),
            'retrograde': False
        }
        
        # Nodo Sur (opuesto al Norte)
        south_node_lon = (node_lon + 180) % 360
        result['points']['South Node'] = {
            'longitude': south_node_lon,
            'latitude': 0.0,
            'distance': 0.0,
            'speed': 0.0,
            'sign': get_zodiac_sign(south_node_lon),
            'position': format_position(south_node_lon),
            'retrograde': False
        }
        
        # Agregar información adicional
        result['location'] = {
            'latitude': datos_usuario['lat'],
            'longitude': datos_usuario['lon'],
            'name': datos_usuario.get('lugar', 'Unknown'),
            'timezone': datos_usuario['zona_horaria']
        }
        
        return result
        
    except Exception as e:
        raise ValueError(f"Error calculando carta natal: {str(e)}")
