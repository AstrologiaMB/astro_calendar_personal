"""
Módulo para el cálculo de cartas natales usando nuestra implementación local de Immanuel.
"""
from datetime import datetime
from typing import Dict, Any
from zoneinfo import ZoneInfo
from ..core.location import Location
from ..immanuel import Subject, Natal

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
