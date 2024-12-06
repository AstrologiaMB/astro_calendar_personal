"""
Módulo para el cálculo de aspectos astrológicos.
"""
from typing import Dict, Optional

def normalize_degrees(degrees: float) -> float:
    """Normaliza los grados a un valor entre 0 y 360."""
    return degrees % 360

def calculate_orb(angle1: float, angle2: float, aspect_angle: float) -> float:
    """
    Calcula el orbe (diferencia) entre dos ángulos considerando un aspecto específico.
    
    Args:
        angle1: Primer ángulo en grados
        angle2: Segundo ángulo en grados
        aspect_angle: Ángulo del aspecto a considerar
        
    Returns:
        Orbe en grados (positivo o negativo)
    """
    # Normalizar ángulos
    a1 = normalize_degrees(angle1)
    a2 = normalize_degrees(angle2)
    
    # Calcular diferencia directa
    diff = a2 - a1
    
    # Ajustar para el camino más corto alrededor del círculo
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    
    # Calcular orbe considerando el aspecto
    orb = diff - aspect_angle
    
    # Ajustar para el camino más corto
    if orb > 180:
        orb -= 360
    elif orb < -180:
        orb += 360
        
    return orb

def calculate_aspect(angle1: float, angle2: float) -> Optional[Dict[str, any]]:
    """
    Calcula el aspecto entre dos posiciones zodiacales.
    
    Args:
        angle1: Primera posición en grados
        angle2: Segunda posición en grados
        
    Returns:
        Dict con información del aspecto o None si no hay aspecto válido
    """
    # Definir aspectos principales y sus ángulos
    aspects = {
        'conjunction': 0,
        'opposition': 180,
        'trine': 120,
        'square': 90,
        'sextile': 60
    }
    
    # Convertir ángulos a float si son strings
    if isinstance(angle1, str):
        angle1 = float(angle1)
    if isinstance(angle2, str):
        angle2 = float(angle2)
    
    # Buscar el aspecto más cercano
    min_orb = float('inf')
    closest_aspect = None
    
    for aspect_name, aspect_angle in aspects.items():
        orb = calculate_orb(angle1, angle2, aspect_angle)
        
        if abs(orb) < abs(min_orb):
            min_orb = orb
            closest_aspect = aspect_name
    
    # Si el orbe es demasiado grande, no hay aspecto válido
    if abs(min_orb) > 10:  # Orbe máximo de 10 grados
        return None
        
    return {
        'type': closest_aspect,
        'orb': min_orb,
        'angle1': normalize_degrees(angle1),
        'angle2': normalize_degrees(angle2)
    }
