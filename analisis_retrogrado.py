import swisseph as swe
from datetime import datetime, timedelta
import pytz
import os
from typing import Dict, List, Tuple

class PlanetaryRetroCalculator:
    def __init__(self):
        ephe_path = os.path.expanduser("~/.local/share/ephe")
        print(f"Configurando Swiss Ephemeris en: {ephe_path}")
        swe.set_ephe_path(ephe_path)
        
        self.SIGNS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
                      "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        
        self.PLANETS = {
            'Mercurio': swe.MERCURY,
            'Venus': swe.VENUS,
            'Marte': swe.MARS,
            'Júpiter': swe.JUPITER,
            'Saturno': swe.SATURN,
            'Urano': swe.URANUS,
            'Neptuno': swe.NEPTUNE,
            'Plutón': swe.PLUTO
        }

        # Diferentes intervalos de búsqueda según el planeta
        self.SEARCH_INTERVALS = {
            'Mercurio': timedelta(hours=6),
            'Venus': timedelta(hours=12),
            'Marte': timedelta(days=1),
            'Júpiter': timedelta(days=2),
            'Saturno': timedelta(days=2),
            'Urano': timedelta(days=2),
            'Neptuno': timedelta(days=2),
            'Plutón': timedelta(days=2)
        }

    def _julian_day(self, date: datetime) -> float:
        return swe.julday(date.year, date.month, date.day, 
                         date.hour + date.minute/60.0 + date.second/3600.0)

    def _format_position(self, lon: float) -> str:
        sign_num = int(lon / 30)
        pos_in_sign = lon % 30
        degrees = int(pos_in_sign)
        minutes = int((pos_in_sign - degrees) * 60)
        return f"{degrees}°{minutes:02d}' {self.SIGNS[sign_num]}"

    def _calculate_speed(self, jd: float, planet_id: int) -> float:
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

    def _calculate_planet_position(self, date: datetime, planet_id: int) -> dict:
        """Calcula posición y velocidad de un planeta"""
        jd = self._julian_day(date)
        result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)[0]
        speed = self._calculate_speed(jd, planet_id)
        
        return {
            'date': date,
            'longitude': result[0],
            'speed': speed,
            'position_str': self._format_position(result[0])
        }

    def _find_station_point(self, start_date: datetime, end_date: datetime, 
                           planet_name: str, is_retrograde_station: bool) -> Dict:
        """Encuentra el punto exacto de estación de un planeta"""
        planet_id = self.PLANETS[planet_name]
        interval = self.SEARCH_INTERVALS[planet_name] / 4  # Intervalo más fino para búsqueda precisa
        
        current_date = start_date
        best_date = None
        min_speed = float('inf')
        
        while current_date <= end_date:
            pos = self._calculate_planet_position(current_date, planet_id)
            speed = abs(pos['speed'])
            
            if speed < min_speed:
                min_speed = speed
                best_date = current_date
            
            current_date += interval
        
        if best_date:
            return self._calculate_planet_position(best_date, planet_id)
        return None

    def analyze_retrogrades(self, year: int):
        """Analiza los períodos retrógrados de todos los planetas"""
        print(f"\nAnalizando retrogradaciones para {year}:")
        
        start_date = datetime(year, 1, 1, tzinfo=pytz.UTC)
        end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
        
        for planet_name, planet_id in self.PLANETS.items():
            print(f"\n=== {planet_name} ===")
            
            current_date = start_date
            was_retrograde = None
            retro_start = None
            interval = self.SEARCH_INTERVALS[planet_name]
            
            while current_date < end_date:
                pos = self._calculate_planet_position(current_date, planet_id)
                is_retrograde = pos['speed'] < 0
                
                if was_retrograde is not None and is_retrograde != was_retrograde:
                    # Encontrar el momento exacto del cambio
                    if is_retrograde:
                        station = self._find_station_point(
                            current_date - interval,
                            current_date + interval,
                            planet_name,
                            True
                        )
                        print(f"\nInicio Retrogradación:")
                        print(f"Fecha: {station['date'].strftime('%d-%B-%Y %H:%M')} UTC")
                        print(f"Posición: {station['position_str']}")
                        print(f"Velocidad: {station['speed']:.4f}°/día")
                        retro_start = station['date']
                    else:
                        station = self._find_station_point(
                            current_date - interval,
                            current_date + interval,
                            planet_name,
                            False
                        )
                        print(f"Fin Retrogradación:")
                        print(f"Fecha: {station['date'].strftime('%d-%B-%Y %H:%M')} UTC")
                        print(f"Posición: {station['position_str']}")
                        print(f"Velocidad: {station['speed']:.4f}°/día")
                        if retro_start:
                            duration = station['date'] - retro_start
                            print(f"Duración: {duration.days} días")
                
                was_retrograde = is_retrograde
                current_date += interval

def main():
    try:
        print("Iniciando análisis de retrogradación planetaria...")
        year = int(input("Ingresa el año para el análisis (ejemplo: 2025): "))
        
        calculator = PlanetaryRetroCalculator()
        calculator.analyze_retrogrades(year)
        
        print("\nAnálisis completado.")
        
    except Exception as e:
        print(f"\nError durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()