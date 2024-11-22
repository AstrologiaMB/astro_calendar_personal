import csv
from typing import List
from ..core.base_event import AstroEvent
from ..core.constants import EventType

class CSVWriter:
    @staticmethod
    def write_events(events: List[AstroEvent], filename: str) -> None:
        """Escribe los eventos en un archivo CSV"""
        # Campos base que todos los eventos tienen
        base_fields = ['fecha_utc', 'hora_utc', 'fecha_local', 'hora_local',
                      'tipo_evento', 'descripcion', 'elevacion', 'azimut']
        
        # Campos adicionales para aspectos
        aspect_fields = ['planeta1', 'planeta2', 'posicion1', 'posicion2',
                        'tipo_aspecto', 'orbe', 'es_aplicativo', 'harmony']
        
        # Campos adicionales para lunas y eclipses
        phase_fields = ['signo', 'grado', 'posicion']
        
        # Combinar todos los campos
        fieldnames = base_fields + aspect_fields + phase_fields

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                # Convertir el evento a diccionario
                event_dict = event.to_dict()
                
                # Asegurar que todos los campos existan (aunque sean vacíos)
                for field in fieldnames:
                    if field not in event_dict:
                        event_dict[field] = ""
                
                writer.writerow(event_dict)
