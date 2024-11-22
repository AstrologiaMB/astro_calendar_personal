import swisseph as swe
from datetime import datetime
import math
import ephem
import pytz
from typing import List, Tuple, Optional
from ..core.constants import EventType
from ..core.base_event import AstroEvent
from ..utils.time_utils import julian_day
from ..utils.math_utils import calculate_planet_position

class EclipseCalculator:
    def __init__(self, observer):
        self.observer = observer

    def calculate_eclipses(self, start_date: datetime, end_date: datetime) -> List[AstroEvent]:
        events = []
        
        # Usar fechas de lunas llenas y nuevas para verificar eclipses
        date = ephem.Date(start_date)
        
        # Verificar eclipses solares en lunas nuevas
        while date < ephem.Date(end_date):
            next_new = ephem.next_new_moon(date)
            if next_new >= ephem.Date(end_date):
                break

            dt = ephem.Date(next_new).datetime()
            dt = pytz.utc.localize(dt)
            
            # Calcular parámetros del eclipse
            jd = julian_day(dt)
            node_distance, eclipse_type = self._get_node_distance_and_type(jd, True)
            
            if eclipse_type:
                self.observer.date = next_new
                sun = ephem.Sun()
                sun.compute(self.observer)
                
                sun_pos = calculate_planet_position(jd, swe.SUN)
                sign_num = int(sun_pos['longitude'] / 30)
                degree = sun_pos['longitude'] % 30
                sign = self._get_sign_name(sign_num)
                
                events.append(AstroEvent(
                    fecha_utc=dt,
                    tipo_evento=EventType.ECLIPSE_SOLAR,
                    descripcion=f"Eclipse Solar {eclipse_type} en {sign} {degree:.2f}° (distancia al nodo: {node_distance:.1f}°)",
                    elevacion=float(sun.alt) * 180/math.pi,
                    azimut=float(sun.az) * 180/math.pi,
                    longitud1=sun_pos['longitude'],  # Agregar longitud para el CSV
                    signo=sign,  # Agregar signo para el CSV
                    grado=degree  # Agregar grado para el CSV
                ))
            
            date = next_new + 1
        
        # Verificar eclipses lunares en lunas llenas
        date = ephem.Date(start_date)
        while date < ephem.Date(end_date):
            next_full = ephem.next_full_moon(date)
            if next_full >= ephem.Date(end_date):
                break

            dt = ephem.Date(next_full).datetime()
            dt = pytz.utc.localize(dt)
            
            # Calcular parámetros del eclipse
            jd = julian_day(dt)
            node_distance, eclipse_type = self._get_node_distance_and_type(jd, False)
            
            if eclipse_type:
                self.observer.date = next_full
                moon = ephem.Moon()
                moon.compute(self.observer)
                
                moon_pos = calculate_planet_position(jd, swe.MOON)
                sign_num = int(moon_pos['longitude'] / 30)
                degree = moon_pos['longitude'] % 30
                sign = self._get_sign_name(sign_num)
                
                events.append(AstroEvent(
                    fecha_utc=dt,
                    tipo_evento=EventType.ECLIPSE_LUNAR,
                    descripcion=f"Eclipse Lunar {eclipse_type} en {sign} {degree:.2f}° (distancia al nodo: {node_distance:.1f}°)",
                    elevacion=float(moon.alt) * 180/math.pi,
                    azimut=float(moon.az) * 180/math.pi,
                    longitud1=moon_pos['longitude'],  # Agregar longitud para el CSV
                    signo=sign,  # Agregar signo para el CSV
                    grado=degree  # Agregar grado para el CSV
                ))
            
            date = next_full + 1
        
        return events

    def _get_node_distance_and_type(self, jd: float, is_solar: bool) -> Tuple[float, Optional[str]]:
        """Calcula la distancia al nodo lunar y determina el tipo de eclipse"""
        # Obtener posiciones
        moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)[0]
        sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0]
        node_pos = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)[0]
        
        # Cálculos básicos
        moon_lon = moon_pos[0]
        moon_lat = abs(moon_pos[1])  # Latitud lunar absoluta
        sun_lon = sun_pos[0]
        node_lon = node_pos[0]
        
        # Calcular distancia al nodo más cercano
        dist_to_north = abs(moon_lon - node_lon)
        dist_to_south = abs(moon_lon - (node_lon + 180))
        
        # Ajustar distancias mayores a 180°
        if dist_to_north > 180:
            dist_to_north = 360 - dist_to_north
        if dist_to_south > 180:
            dist_to_south = 360 - dist_to_south
        
        # Determinar la distancia al nodo más cercano
        if dist_to_north <= dist_to_south:
            node_distance = dist_to_north
            signed_distance = node_distance
        else:
            node_distance = dist_to_south
            signed_distance = -node_distance
        
        # Determinar tipo de eclipse según criterios
        if is_solar:
            return self._get_solar_eclipse_type(node_distance, moon_lat, signed_distance)
        else:
            return self._get_lunar_eclipse_type(node_distance, moon_lat, sun_lon, moon_lon, signed_distance)

    def _get_solar_eclipse_type(self, node_distance: float, moon_lat: float, signed_distance: float) -> Tuple[float, Optional[str]]:
        """Determina el tipo de eclipse solar"""
        if node_distance > 18.5:
            return signed_distance, None
            
        if moon_lat > 1.5:
            return signed_distance, None
            
        if node_distance <= 10:
            if moon_lat <= 0.5:
                return signed_distance, "Total"
            elif moon_lat <= 0.9:
                return signed_distance, "Anular"
            elif moon_lat <= 1.2:
                return signed_distance, "Parcial"
        elif node_distance <= 18.5:
            return signed_distance, "Parcial"
            
        return signed_distance, None

    def _get_lunar_eclipse_type(self, node_distance: float, moon_lat: float, sun_lon: float, 
                              moon_lon: float, signed_distance: float) -> Tuple[float, Optional[str]]:
        """Determina el tipo de eclipse lunar"""
        if node_distance > 12.5:
            return signed_distance, None
            
        if moon_lat > 1.0:
            return signed_distance, None
            
        elong = abs(moon_lon - (sun_lon + 180))
        if elong > 180:
            elong = 360 - elong
            
        if node_distance <= 3.8:
            if moon_lat <= 0.5:
                return signed_distance, "Total"
            elif moon_lat <= 0.7:
                return signed_distance, "Parcial"
        elif node_distance <= 6:
            if moon_lat <= 0.85:
                return signed_distance, "Parcial"
        elif node_distance <= 12.5:
            if moon_lat <= 1.0 and elong >= 175:
                return signed_distance, "Penumbral"
                
        return signed_distance, None

    def _get_sign_name(self, sign_num: int) -> str:
        """Obtiene el nombre del signo zodiacal"""
        from ..core.constants import AstronomicalConstants
        return AstronomicalConstants.SIGNS[sign_num]
