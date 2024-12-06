"""
Módulo para el análisis astrológico de eclipses y su impacto en cartas natales.
"""
from datetime import datetime
from typing import Dict, List, Any
import swisseph as swe
from .eclipses import EclipseCalculator
from .aspects import calculate_aspect
from ..core.base_event import AstroEvent
from ..core.constants import EventType

class EclipseAnalyzer:
    """Clase para analizar el impacto astrológico de eclipses en una carta natal."""
    
    def __init__(self, natal_chart: Dict[str, Any]):
        """
        Inicializa el analizador con una carta natal.
        
        Args:
            natal_chart: Diccionario con los datos de la carta natal
        """
        self.natal_chart = natal_chart
        self.orbs = {
            'conjunction': 8.0,  # Orbe para conjunciones con eclipses
            'opposition': 8.0,   # Orbe para oposiciones con eclipses
            'square': 7.0,       # Orbe para cuadraturas con eclipses
            'trine': 7.0,        # Orbe para trígonos con eclipses
        }

    def analyze_eclipse_impact(self, eclipse: AstroEvent) -> Dict[str, Any]:
        """
        Analiza el impacto de un eclipse en la carta natal.
        
        Args:
            eclipse: Evento de eclipse a analizar
            
        Returns:
            Dict con el análisis del impacto del eclipse
        """
        impact = {
            'fecha_utc': eclipse.fecha_utc.isoformat(),
            'tipo': eclipse.tipo_evento,
            'posicion': {
                'longitud': eclipse.longitud1,
                'signo': eclipse.signo,
                'grado': eclipse.grado
            },
            'casa_activada': self._get_activated_house(eclipse.longitud1),
            'aspectos': self._analyze_aspects(eclipse.longitud1),
            'nodos': self._analyze_node_relationship(eclipse.longitud1)
        }
        
        return impact

    def _get_activated_house(self, eclipse_lon: float) -> Dict[str, Any]:
        """
        Determina la casa astrológica activada por el eclipse.
        
        Args:
            eclipse_lon: Longitud zodiacal del eclipse
            
        Returns:
            Dict con información sobre la casa activada
        """
        # Normalizar la longitud del eclipse a 0-360
        eclipse_lon = eclipse_lon % 360
        
        # Obtener las posiciones de las casas
        house_positions = []
        for i in range(1, 13):
            house_data = self.natal_chart['houses'][i]
            house_positions.append((i, house_data['longitude']))
        
        # Ordenar las casas por posición
        house_positions.sort(key=lambda x: x[1])
        
        # Encontrar la casa que contiene la longitud del eclipse
        for i in range(len(house_positions)):
            current_house, current_pos = house_positions[i]
            next_house, next_pos = house_positions[(i + 1) % 12]
            
            # Si la siguiente posición es menor que la actual, estamos cruzando 0°
            if next_pos < current_pos:
                if eclipse_lon >= current_pos or eclipse_lon < next_pos:
                    return {
                        'numero': current_house,
                        'cuspide': current_pos,
                        'siguiente_cuspide': next_pos,
                        'signo': self.natal_chart['houses'][current_house]['sign']
                    }
            else:
                if current_pos <= eclipse_lon < next_pos:
                    return {
                        'numero': current_house,
                        'cuspide': current_pos,
                        'siguiente_cuspide': next_pos,
                        'signo': self.natal_chart['houses'][current_house]['sign']
                    }
        
        # Si llegamos aquí, el eclipse está en la última casa antes de 0°
        last_house, last_pos = house_positions[-1]
        first_house, first_pos = house_positions[0]
        return {
            'numero': last_house,
            'cuspide': last_pos,
            'siguiente_cuspide': first_pos,
            'signo': self.natal_chart['houses'][last_house]['sign']
        }

    def _analyze_aspects(self, eclipse_lon: float) -> List[Dict[str, Any]]:
        """
        Analiza los aspectos del eclipse con planetas natales.
        
        Args:
            eclipse_lon: Longitud zodiacal del eclipse
            
        Returns:
            Lista de aspectos encontrados
        """
        aspectos = []
        points = self.natal_chart['points']
        
        for planeta, datos in points.items():
            if planeta in ['Vertex', 'Part of Fortune', 'Asc', 'Mc', 'South Node']:
                continue
                
            lon_planeta = float(datos['longitude'])
            aspecto = calculate_aspect(eclipse_lon, lon_planeta)
            
            if aspecto and aspecto['type'] in self.orbs:
                if abs(aspecto['orb']) <= self.orbs[aspecto['type']]:
                    aspectos.append({
                        'planeta': planeta,
                        'tipo': aspecto['type'],
                        'orbe': aspecto['orb']
                    })
        
        return aspectos

    def _analyze_node_relationship(self, eclipse_lon: float) -> Dict[str, Any]:
        """
        Analiza la relación del eclipse con los nodos lunares natales.
        
        Args:
            eclipse_lon: Longitud zodiacal del eclipse
            
        Returns:
            Dict con información sobre la relación con los nodos
        """
        nodo_norte = float(self.natal_chart['points']['North Node']['longitude'])
        nodo_sur = float(self.natal_chart['points']['South Node']['longitude'])
        
        # Calcular distancias a los nodos
        dist_norte = min(abs(eclipse_lon - nodo_norte), 
                        360 - abs(eclipse_lon - nodo_norte))
        dist_sur = min(abs(eclipse_lon - nodo_sur), 
                      360 - abs(eclipse_lon - nodo_sur))
        
        return {
            'distancia_nodo_norte': dist_norte,
            'distancia_nodo_sur': dist_sur,
            'conjuncion_nodo': dist_norte <= 8 or dist_sur <= 8
        }

def analizar_eclipses_periodo(natal_chart: Dict[str, Any], 
                            start_date: datetime,
                            end_date: datetime,
                            location: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analiza todos los eclipses en un período y su impacto en una carta natal.
    
    Args:
        natal_chart: Carta natal a analizar
        start_date: Fecha inicial del período
        end_date: Fecha final del período
        location: Diccionario con datos de ubicación (lat, lon)
        
    Returns:
        Lista de análisis de impacto de eclipses
    """
    # Crear calculador de eclipses
    from ephem import Observer
    observer = Observer()
    observer.lat = str(location['latitude'])
    observer.lon = str(location['longitude'])
    
    calculator = EclipseCalculator(observer)
    analyzer = EclipseAnalyzer(natal_chart)
    
    # Obtener eclipses del período
    eclipses = calculator.calculate_eclipses(start_date, end_date)
    
    # Analizar cada eclipse
    resultados = []
    for eclipse in eclipses:
        impacto = analyzer.analyze_eclipse_impact(eclipse)
        resultados.append(impacto)
    
    return resultados
