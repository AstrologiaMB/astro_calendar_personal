"""
Módulo para calcular eventos lunares (lunas nuevas y llenas) y su posición en las casas natales.
"""
from datetime import datetime
from typing import List, Dict, Any
from .lunar_phases import LunarPhaseCalculator
from .natal_chart import calcular_carta_natal
from ..core.base_event import AstroEvent

class LunarCalendarCalculator:
    def __init__(self, datos_natal: Dict[str, Any]):
        """
        Inicializa el calculador de calendario lunar.
        
        Args:
            datos_natal: Diccionario con los datos natales del usuario:
                - hora_local: str (formato ISO)
                - lat: float
                - lon: float
                - zona_horaria: str
        """
        self.datos_natal = datos_natal
        # Calcular carta natal una sola vez
        self.carta_natal = calcular_carta_natal(datos_natal)
        
    def _determinar_casa(self, longitud: float) -> int:
        """
        Determina en qué casa cae una longitud zodiacal.
        
        Args:
            longitud: Longitud zodiacal en grados (0-360)
            
        Returns:
            Número de casa (1-12)
        """
        casas = self.carta_natal['houses']
        
        # Convertir el diccionario de casas a una lista ordenada
        cusps = [(i, float(casas[i]['longitude'])) for i in range(1, 13)]
        cusps.sort(key=lambda x: x[1])
        
        # Encontrar la casa correspondiente
        for i in range(len(cusps)):
            cusp_actual = cusps[i][1]
            cusp_siguiente = cusps[(i + 1) % 12][1]
            
            # Manejar el caso especial cuando cruzamos 0°
            if cusp_siguiente < cusp_actual:
                if longitud >= cusp_actual or longitud < cusp_siguiente:
                    return cusps[i][0]
            else:
                if cusp_actual <= longitud < cusp_siguiente:
                    return cusps[i][0]
                    
        # Si no se encontró (no debería ocurrir), devolver la primera casa
        return 1
        
    def calcular_eventos_lunares(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict[str, Any]]:
        """
        Calcula eventos lunares y su posición en las casas natales.
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            
        Returns:
            Lista de eventos lunares con información de casa natal
        """
        # Crear calculador de fases lunares
        from ephem import Observer
        observer = Observer()
        observer.lat = str(self.datos_natal['lat'])
        observer.lon = str(self.datos_natal['lon'])
        observer.elevation = 0
        
        lunar_calc = LunarPhaseCalculator(observer)
        
        # Obtener eventos lunares básicos
        eventos = lunar_calc.calculate_phases(fecha_inicio, fecha_fin)
        
        # Enriquecer eventos con información de casas
        eventos_enriquecidos = []
        for evento in eventos:
            # Determinar casa del evento
            casa = self._determinar_casa(evento.longitud1)
            
            # Crear diccionario con toda la información
            evento_dict = {
                'fecha_utc': evento.fecha_utc,
                'tipo': evento.tipo_evento,
                'signo': evento.signo,
                'grado': evento.grado,
                'casa': casa,
                'descripcion': f"{evento.descripcion} en Casa {casa}"
            }
            
            eventos_enriquecidos.append(evento_dict)
            
        return eventos_enriquecidos
