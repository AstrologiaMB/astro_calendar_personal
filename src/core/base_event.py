from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from zoneinfo import ZoneInfo
from .constants import EventType, AstronomicalConstants

@dataclass
class AstroEvent:
    """Clase base para eventos astronómicos"""
    fecha_utc: datetime
    tipo_evento: EventType
    descripcion: str
    elevacion: Optional[float] = None
    azimut: Optional[float] = None
    # Campos para aspectos
    planeta1: Optional[str] = None
    planeta2: Optional[str] = None
    longitud1: Optional[float] = None
    longitud2: Optional[float] = None
    velocidad1: Optional[float] = None
    velocidad2: Optional[float] = None
    tipo_aspecto: Optional[str] = None
    orbe: Optional[float] = None
    es_aplicativo: Optional[bool] = None
    # Campos para signos y grados
    signo: Optional[str] = None
    grado: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Inicialización posterior con validaciones y cálculos adicionales"""
        # Convertir a hora local (Buenos Aires)
        tz_bsas = ZoneInfo("America/Argentina/Buenos_Aires")
        self.fecha_local = self.fecha_utc.astimezone(tz_bsas)
        
        # Para aspectos, calcular datos adicionales
        if self.tipo_evento == EventType.ASPECTO:
            self._calculate_aspect_details()

    def _calculate_aspect_details(self):
        """Calcula detalles adicionales para aspectos"""
        if self.tipo_evento == EventType.ASPECTO and self.longitud1 is not None and self.longitud2 is not None:
            # Calcular signos zodiacales
            self.signo1 = AstronomicalConstants.get_sign_name(self.longitud1)
            self.signo2 = AstronomicalConstants.get_sign_name(self.longitud2)
            
            # Calcular grados en signo
            self.grado1 = self.longitud1 % 30
            self.grado2 = self.longitud2 % 30

    def format_position(self, longitude: float) -> str:
        """Formatea una posición zodiacal"""
        sign = AstronomicalConstants.get_sign_name(longitude)
        degrees = int(longitude % 30)
        minutes = int((longitude % 30 - degrees) * 60)
        return f"{degrees}°{minutes:02d}' {sign}"

    def to_dict(self) -> dict:
        """Convierte el evento a un diccionario para CSV"""
        base_dict = {
            'fecha_utc': self.fecha_utc.strftime('%Y-%m-%d'),
            'hora_utc': self.fecha_utc.strftime('%H:%M'),
            'fecha_local': self.fecha_local.strftime('%Y-%m-%d'),
            'hora_local': self.fecha_local.strftime('%H:%M'),
            'tipo_evento': self.tipo_evento.value,
            'descripcion': self.descripcion,
            'elevacion': f"{self.elevacion:.1f}°" if self.elevacion is not None else "",
            'azimut': f"{self.azimut:.1f}°" if self.azimut is not None else ""
        }
        
        # Añadir campos específicos de aspectos si es necesario
        if self.tipo_evento == EventType.ASPECTO:
            aspect_dict = {
                'planeta1': self.planeta1,
                'planeta2': self.planeta2,
                'posicion1': self.format_position(self.longitud1) if self.longitud1 is not None else "",
                'posicion2': self.format_position(self.longitud2) if self.longitud2 is not None else "",
                'tipo_aspecto': self.tipo_aspecto,
                'orbe': f"{self.orbe:.2f}°" if self.orbe is not None else "",
                'es_aplicativo': "Sí" if self.es_aplicativo else "No"
            }
            base_dict.update(aspect_dict)
        
        # Añadir campos de signo y grado para lunas y eclipses
        elif self.tipo_evento in [EventType.LUNA_NUEVA, EventType.LUNA_LLENA, 
                                EventType.ECLIPSE_SOLAR, EventType.ECLIPSE_LUNAR]:
            if self.signo is not None and self.grado is not None:
                phase_dict = {
                    'signo': self.signo,
                    'grado': f"{self.grado:.2f}°",
                    'posicion': self.format_position(self.longitud1) if self.longitud1 is not None else ""
                }
                base_dict.update(phase_dict)
            
        # Añadir metadata adicional
        base_dict.update(self.metadata)
        
        return base_dict
