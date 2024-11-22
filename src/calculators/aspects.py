from datetime import datetime, timedelta
from typing import List, Dict, Optional
import swisseph as swe
from ..core.constants import EventType, AstronomicalConstants
from ..core.base_event import AstroEvent
from ..utils.time_utils import julian_day, find_exact_time
from ..utils.math_utils import calculate_planet_position

class AspectCalculator:
    def __init__(self):
        self.aspects = AstronomicalConstants.ASPECTS
        self.planets = AstronomicalConstants.PLANETS
        self.planets_info = AstronomicalConstants.PLANETS_INFO

    def _get_planet_id(self, planet_name: str) -> int:
        return self.planets[planet_name][0]

    def _get_planet_speed(self, planet_name: str) -> float:
        speed = self.planets_info[planet_name]['mean_speed']
        if isinstance(speed, list):
            return max(abs(speed[0]), abs(speed[1]))
        return abs(speed)

    def _get_aspect_orb(self, aspect_name: str, p1_name: str, p2_name: str) -> float:
        orb1 = self.planets_info[p1_name]['orb_major']
        orb2 = self.planets_info[p2_name]['orb_major']
        base_orb = max(orb1, orb2)
        return base_orb * self.aspects[aspect_name]['orb_factor']

    def _normalize_angle(self, angle: float) -> float:
        return angle % 360

    def _calculate_aspect_difference(self, lon1: float, lon2: float, aspect_angle: float) -> float:
        lon1 = self._normalize_angle(lon1)
        lon2 = self._normalize_angle(lon2)
        
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff
            
        return abs(diff - aspect_angle)

    def _get_precise_position(self, jd: float, planet_id: int) -> Dict[str, float]:
        """Obtiene posición planetaria con alta precisión"""
        try:
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            data, flags = swe.calc_ut(jd, planet_id, flags)
            return {
                'longitude': data[0],
                'latitude': data[1],
                'distance': data[2],
                'speed': data[3]
            }
        except Exception:
            # Si hay algún error, usar el método original
            return calculate_planet_position(jd, planet_id)

    def _is_aspect_applying(self, jd: float, p1_name: str, p2_name: str, 
                          p1_id: int, p2_id: int, aspect_angle: float) -> bool:
        pos1 = self._get_precise_position(jd, p1_id)
        pos2 = self._get_precise_position(jd, p2_id)
        
        curr_diff = self._calculate_aspect_difference(
            pos1['longitude'], 
            pos2['longitude'],
            aspect_angle
        )
        
        # Usar intervalo más pequeño para mayor precisión
        future_jd = jd + 1/1440  # 1 minuto después
        pos1_future = self._get_precise_position(future_jd, p1_id)
        pos2_future = self._get_precise_position(future_jd, p2_id)
        
        future_diff = self._calculate_aspect_difference(
            pos1_future['longitude'],
            pos2_future['longitude'],
            aspect_angle
        )
        
        return future_diff < curr_diff

    def _find_exact_aspect_time(self, 
                             start_date: datetime,
                             p1_name: str,
                             p2_name: str,
                             aspect_name: str) -> Optional[Dict]:
        aspect_angle = self.aspects[aspect_name]['angle']
        p1_id = self._get_planet_id(p1_name)
        p2_id = self._get_planet_id(p2_name)
        
        # Ventanas de búsqueda mejoradas para planetas lentos
        v1 = self._get_planet_speed(p1_name)
        v2 = self._get_planet_speed(p2_name)
        velocidad_total = v1 + v2
        
        # Ventanas más amplias para capturar aspectos
        if velocidad_total > 10:
            search_window = timedelta(hours=6)
        elif velocidad_total > 2:
            search_window = timedelta(hours=12)
        elif velocidad_total > 0.5:
            search_window = timedelta(days=1)
        else:
            search_window = timedelta(days=2)

        end_date = start_date + search_window
        
        def aspect_condition(date: datetime) -> float:
            jd = julian_day(date)
            pos1 = self._get_precise_position(jd, p1_id)
            pos2 = self._get_precise_position(jd, p2_id)
            return self._calculate_aspect_difference(
                pos1['longitude'],
                pos2['longitude'],
                aspect_angle
            )
        
        exact_date, min_diff = find_exact_time(
            start_date,
            end_date,
            aspect_condition,
            tolerance=timedelta(seconds=1)  # Aumentar precisión a 1 segundo
        )
        
        if not exact_date:
            return None

        orb = self._get_aspect_orb(aspect_name, p1_name, p2_name)
        if min_diff > orb:
            return None
            
        jd_exact = julian_day(exact_date)
        pos1_exact = self._get_precise_position(jd_exact, p1_id)
        pos2_exact = self._get_precise_position(jd_exact, p2_id)
        
        is_applying = self._is_aspect_applying(
            jd_exact, p1_name, p2_name, p1_id, p2_id, aspect_angle
        )
        
        return {
            'date': exact_date,
            'positions': (pos1_exact, pos2_exact),
            'difference': min_diff,
            'is_applying': is_applying
        }

    def calculate_aspects(self, start_date: datetime, end_date: datetime) -> List[AstroEvent]:
        events = []
        processed_aspects = set()

        # Filtrar planetas excluyendo la Luna
        planet_names = [name for name in self.planets.keys() if name != 'Luna']
        
        # Crear pares de planetas
        planet_pairs = []
        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                planet_pairs.append((planet_names[i], planet_names[j]))

        for p1_name, p2_name in planet_pairs:
            current_date = start_date
            
            while current_date < end_date:
                for aspect_name in self.aspects:
                    # Usar un ID más específico basado en la diferencia angular real
                    jd = julian_day(current_date)
                    pos1 = self._get_precise_position(jd, self._get_planet_id(p1_name))
                    pos2 = self._get_precise_position(jd, self._get_planet_id(p2_name))
                    diff = self._calculate_aspect_difference(
                        pos1['longitude'],
                        pos2['longitude'],
                        self.aspects[aspect_name]['angle']
                    )
                    
                    # Solo proceder si la diferencia es menor que el orbe
                    if diff <= self._get_aspect_orb(aspect_name, p1_name, p2_name):
                        exact_info = self._find_exact_aspect_time(
                            current_date,
                            p1_name,
                            p2_name,
                            aspect_name
                        )

                        if exact_info:
                            # Verificar que no haya un aspecto similar ya procesado
                            aspect_time = exact_info['date']
                            is_new_aspect = True
                            
                            for processed_time in [t for t in processed_aspects if t[0] == p1_name and t[1] == p2_name and t[2] == aspect_name]:
                                time_diff = abs((aspect_time - processed_time[3]).total_seconds())
                                if time_diff < 43200:  # 12 horas
                                    is_new_aspect = False
                                    break
                            
                            if is_new_aspect:
                                pos1, pos2 = exact_info['positions']
                                
                                event = AstroEvent(
                                    fecha_utc=exact_info['date'],
                                    tipo_evento=EventType.ASPECTO,
                                    descripcion=f"{p1_name} en {aspect_name} con {p2_name}",
                                    planeta1=p1_name,
                                    planeta2=p2_name,
                                    longitud1=pos1['longitude'],
                                    longitud2=pos2['longitude'],
                                    velocidad1=pos1['speed'],
                                    velocidad2=pos2['speed'],
                                    tipo_aspecto=aspect_name,
                                    orbe=exact_info['difference'],
                                    es_aplicativo=exact_info['is_applying'],
                                    metadata={
                                        'harmony': self.aspects[aspect_name]['harmony']
                                    }
                                )
                                
                                events.append(event)
                                processed_aspects.add((p1_name, p2_name, aspect_name, aspect_time))

                # Intervalo fijo de 5 minutos para mayor precisión
                current_date += timedelta(minutes=5)

        return sorted(events, key=lambda x: x.fecha_utc)
