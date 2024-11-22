import swisseph as swe
from typing import Dict
from datetime import datetime

def calculate_speed(jd: float, planet_id: int) -> float:
    """Calcula la velocidad del planeta usando dos posiciones cercanas"""
    pos1 = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)[0]
    pos2 = swe.calc_ut(jd + 1/24, planet_id, swe.FLG_SWIEPH)[0]  # 1 hora después
    
    # Manejar el cruce del punto 0°
    diff = pos2[0] - pos1[0]
    if abs(diff) > 180:
        if diff > 0:
            diff = diff - 360
        else:
            diff = diff + 360
            
    return diff * 24

def calculate_planet_position(jd: float, planet_id: int) -> Dict[str, float]:
    """Calcula posición planetaria usando Swiss Ephemeris"""
    result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)[0]
    speed = calculate_speed(jd, planet_id)

    return {
        'longitude': result[0],
        'latitude': result[1],
        'distance': result[2],
        'speed': speed
    }

def format_position(lon: float) -> str:
    """Formatea la longitud eclíptica"""
    from src.core.constants import AstronomicalConstants
    sign_num = int(lon / 30)
    pos_in_sign = lon % 30
    degrees = int(pos_in_sign)
    minutes = int((pos_in_sign - degrees) * 60)
    return f"{degrees}°{minutes:02d}' {AstronomicalConstants.SIGNS[sign_num]}"