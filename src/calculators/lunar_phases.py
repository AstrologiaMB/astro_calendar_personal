import ephem
from datetime import datetime
import pytz
import math
from typing import List
from ..core.constants import EventType, AstronomicalConstants
from ..core.base_event import AstroEvent
from ..utils.time_utils import julian_day
from ..utils.math_utils import calculate_planet_position
import swisseph as swe

class LunarPhaseCalculator:
    def __init__(self, observer):
        self.observer = observer

    def calculate_phases(self, start_date: datetime, end_date: datetime) -> List[AstroEvent]:
        events = []
        
        # Calcular lunas llenas
        date = ephem.Date(start_date)
        while date < ephem.Date(end_date):
            next_full = ephem.next_full_moon(date)
            if next_full >= ephem.Date(end_date):
                break

            self.observer.date = next_full
            moon = ephem.Moon()
            moon.compute(self.observer)

            dt = ephem.Date(next_full).datetime()
            dt = pytz.utc.localize(dt)

            # Calcular posición exacta para el signo y grado
            jd = julian_day(dt)
            moon_pos = calculate_planet_position(jd, swe.MOON)
            sign_num = int(moon_pos['longitude'] / 30)
            degree = moon_pos['longitude'] % 30

            events.append(AstroEvent(
                fecha_utc=dt,
                tipo_evento=EventType.LUNA_LLENA,
                descripcion=f"Luna llena en {AstronomicalConstants.SIGNS[sign_num]} {degree:.2f}°",
                elevacion=float(moon.alt) * 180/math.pi,
                azimut=float(moon.az) * 180/math.pi,
                longitud1=moon_pos['longitude'],  # Agregar longitud para el CSV
                signo=AstronomicalConstants.SIGNS[sign_num],  # Agregar signo para el CSV
                grado=degree  # Agregar grado para el CSV
            ))

            date = next_full + 1

        # Calcular lunas nuevas
        date = ephem.Date(start_date)
        while date < ephem.Date(end_date):
            next_new = ephem.next_new_moon(date)
            if next_new >= ephem.Date(end_date):
                break

            self.observer.date = next_new
            sun = ephem.Sun()
            sun.compute(self.observer)

            dt = ephem.Date(next_new).datetime()
            dt = pytz.utc.localize(dt)

            # Calcular posición exacta para el signo y grado
            jd = julian_day(dt)
            sun_pos = calculate_planet_position(jd, swe.SUN)
            sign_num = int(sun_pos['longitude'] / 30)
            degree = sun_pos['longitude'] % 30

            events.append(AstroEvent(
                fecha_utc=dt,
                tipo_evento=EventType.LUNA_NUEVA,
                descripcion=f"Luna nueva en {AstronomicalConstants.SIGNS[sign_num]} {degree:.2f}°",
                elevacion=float(sun.alt) * 180/math.pi,
                azimut=float(sun.az) * 180/math.pi,
                longitud1=sun_pos['longitude'],  # Agregar longitud para el CSV
                signo=AstronomicalConstants.SIGNS[sign_num],  # Agregar signo para el CSV
                grado=degree  # Agregar grado para el CSV
            ))

            date = next_new + 1

        return events
