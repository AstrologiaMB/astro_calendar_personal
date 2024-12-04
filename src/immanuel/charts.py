"""
Chart calculation module.
Adapted from Immanuel for local use.
"""
import swisseph as swe
from datetime import datetime
from typing import Dict, Any, Optional

class Subject:
    """Class representing a subject for astrological calculations."""
    
    def __init__(self, date_time: str, latitude: str, longitude: str):
        """
        Initialize a subject.
        
        Args:
            date_time: Date and time in format 'YYYY-MM-DD HH:MM'
            latitude: Latitude in format '12.34n' or '12.34s'
            longitude: Longitude in format '12.34e' or '12.34w'
        """
        self.date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
        
        # Parse latitude
        self.latitude = float(latitude[:-1])
        if latitude[-1].lower() == 's':
            self.latitude = -self.latitude
            
        # Parse longitude
        self.longitude = float(longitude[:-1])
        if longitude[-1].lower() == 'w':
            self.longitude = -self.longitude
            
        # Convert to Julian day
        self.julian_day = swe.julday(
            self.date_time.year,
            self.date_time.month,
            self.date_time.day,
            self.date_time.hour + self.date_time.minute/60.0
        )

class Natal:
    """Class for calculating natal charts."""
    
    PLANETS = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Uranus': swe.URANUS,
        'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO
    }
    
    SIGNS = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    
    def __init__(self, subject: Subject):
        """
        Initialize natal chart calculation.
        
        Args:
            subject: Subject instance with birth data
        """
        self.subject = subject
        self.points = {}
        self.houses = {}
        
        # Set ephemeris path if needed
        # swe.set_ephe_path()  # Commented out as pyswisseph includes its own ephemeris
        
        # Calculate positions
        self._calculate_points()
        self._calculate_houses()
        
    def _normalize_degrees(self, degrees: float) -> float:
        """Normalize degrees to 0-360 range."""
        return float(degrees) % 360
        
    def _get_sign_and_position(self, longitude: float) -> tuple[str, float]:
        """Get zodiac sign and position within sign."""
        norm_lon = self._normalize_degrees(longitude)
        sign_num = int(norm_lon / 30)
        position = norm_lon % 30
        return self.SIGNS[sign_num], position
        
    def _calculate_points(self):
        """Calculate planetary positions."""
        for name, planet_id in self.PLANETS.items():
            # Get position
            flags = swe.FLG_SWIEPH
            result, flag = swe.calc_ut(self.subject.julian_day, planet_id, flags)
            
            # Get longitude and check if retrograde
            longitude = self._normalize_degrees(result[0])
            speed = result[3]
            is_retrograde = speed < 0
            
            # Get sign and position
            sign, position = self._get_sign_and_position(longitude)
            
            self.points[name] = {
                'longitude': longitude,
                'latitude': result[1],
                'distance': result[2],
                'speed': speed,
                'sign': sign,
                'position': f"{int(position)}°{int((position % 1) * 60):02d}'",
                'retrograde': is_retrograde
            }
            
    def _calculate_houses(self):
        """Calculate house cusps."""
        # Calculate house cusps
        cusps, ascmc = swe.houses(
            self.subject.julian_day,
            self.subject.latitude,
            self.subject.longitude,
            b'P'  # Placidus house system
        )
        
        # Store Ascendant and Midheaven
        asc_lon = self._normalize_degrees(ascmc[0])
        mc_lon = self._normalize_degrees(ascmc[1])
        
        sign, pos = self._get_sign_and_position(asc_lon)
        self.points['Asc'] = {
            'longitude': asc_lon,
            'sign': sign,
            'position': f"{int(pos)}°{int((pos % 1) * 60):02d}'"
        }
        
        sign, pos = self._get_sign_and_position(mc_lon)
        self.points['Mc'] = {
            'longitude': mc_lon,
            'sign': sign,
            'position': f"{int(pos)}°{int((pos % 1) * 60):02d}'"
        }
        
        # Store house cusps
        for i in range(12):
            cusp_lon = self._normalize_degrees(cusps[i])
            sign, pos = self._get_sign_and_position(cusp_lon)
            self.houses[i+1] = {
                'longitude': cusp_lon,
                'sign': sign,
                'position': f"{int(pos)}°{int((pos % 1) * 60):02d}'"
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert natal chart to dictionary."""
        return {
            'points': self.points,
            'houses': self.houses
        }
