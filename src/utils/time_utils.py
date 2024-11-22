from datetime import datetime, timedelta
from typing import Callable, Tuple
import swisseph as swe

def julian_day(date: datetime) -> float:
    """Convierte datetime a día juliano"""
    return swe.julday(date.year, date.month, date.day,
                     date.hour + date.minute/60.0 + date.second/3600.0)

def find_exact_time(
    start_date: datetime,
    end_date: datetime,
    condition_func: Callable[[datetime], float],
    tolerance: timedelta = timedelta(seconds=30)  # Reducido a 30 segundos
) -> Tuple[datetime, float]:
    """
    Encuentra el momento exacto en que una condición alcanza su valor mínimo.
    
    Args:
        start_date: Fecha inicial de búsqueda
        end_date: Fecha final de búsqueda
        condition_func: Función que evalúa la condición, retorna un float
        tolerance: Tolerancia mínima en tiempo
    
    Returns:
        Tuple[datetime, float]: Fecha exacta y el valor mínimo encontrado
    """
    best_date = start_date
    min_value = condition_func(start_date)
    
    # Búsqueda binaria mejorada
    while (end_date - start_date) > tolerance:
        # Evaluar tres puntos equidistantes
        span = end_date - start_date
        third = span / 3
        
        point1 = start_date + third
        point2 = start_date + (2 * third)
        
        val1 = condition_func(point1)
        val2 = condition_func(point2)
        
        # Actualizar el mínimo si encontramos un mejor valor
        if val1 < min_value:
            min_value = val1
            best_date = point1
        if val2 < min_value:
            min_value = val2
            best_date = point2
            
        # Determinar el intervalo que contiene el mínimo
        start_val = condition_func(start_date)
        end_val = condition_func(end_date)
        
        if val1 < val2:
            if val1 < start_val:
                end_date = point2
            else:
                end_date = point1
        else:
            if val2 < val1:
                if val2 < end_val:
                    start_date = point1
                else:
                    start_date = point2
            else:
                # Si los valores son iguales, reducir ambos lados
                start_date = point1
                end_date = point2
    
    # Refinamiento final usando interpolación
    if start_date != end_date:
        start_val = condition_func(start_date)
        end_val = condition_func(end_date)
        
        if start_val < min_value:
            min_value = start_val
            best_date = start_date
        if end_val < min_value:
            min_value = end_val
            best_date = end_date
            
        # Interpolación parabólica para mayor precisión
        mid_date = start_date + (end_date - start_date) / 2
        mid_val = condition_func(mid_date)
        
        if mid_val < min_value:
            min_value = mid_val
            best_date = mid_date
            
            # Ajuste fino usando los tres puntos
            denom = (start_val - 2*mid_val + end_val)
            if abs(denom) > 1e-10:
                alpha = 0.5 * (start_val - end_val) / denom
                if 0 < alpha < 1:
                    interp_date = start_date + alpha * (end_date - start_date)
                    interp_val = condition_func(interp_date)
                    if interp_val < min_value:
                        min_value = interp_val
                        best_date = interp_date
    
    return best_date, min_value

def interpolate_time(
    time1: datetime,
    time2: datetime,
    val1: float,
    val2: float,
    target: float
) -> datetime:
    """
    Interpola linealmente entre dos tiempos basado en sus valores.
    
    Args:
        time1: Primer tiempo
        time2: Segundo tiempo
        val1: Valor en time1
        val2: Valor en time2
        target: Valor objetivo
    
    Returns:
        datetime: Tiempo interpolado
    """
    if abs(val2 - val1) < 1e-10:  # Evitar división por cero
        return time1
        
    # Interpolación mejorada usando spline cúbico
    h = (time2 - time1).total_seconds()
    t = (target - val1) / (val2 - val1)
    
    # Ajuste no lineal para mejor precisión cerca de los extremos
    if t < 0.1:
        t = t * (1.0 + 0.1 * (1.0 - t))
    elif t > 0.9:
        t = t * (1.0 - 0.1 * t)
        
    return time1 + timedelta(seconds=h * t)
