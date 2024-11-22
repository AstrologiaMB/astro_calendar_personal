import csv
from icalendar import Calendar, Event
from datetime import datetime, timezone
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, Optional
from pathlib import Path
import logging
from dataclasses import dataclass

@dataclass
class EventoAstrologico:
    fecha_utc: datetime
    tipo_evento: str
    descripcion: str
    explicacion_personal: str
    explicacion_mundana: str

class AstroCalendarConverter:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.simbolos: Dict[str, str] = {
            # Planetas
            'Luna': '☽', 'Sol': '☉', 'Mercurio': '☿', 'Venus': '♀', 
            'Marte': '♂', 'Jupiter': '♃', 'Saturno': '♄', 'Urano': '♅',
            'Neptuno': '♆', 'Pluton': '♇', 'Nodo Norte': '☊', 'Nodo Sur': '☋',
            
            # Signos
            'Aries': '♈', 'Tauro': '♉', 'Geminis': '♊', 'Cancer': '♋',
            'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Escorpio': '♏',
            'Sagitario': '♐', 'Capricornio': '♑', 'Acuario': '♒', 'Piscis': '♓',
            
            # Aspectos
            'Oposicion': '☍', 'Cuadratura': '□', 'Trigono': '△',
            'Sextil': '⚹', 'Conjuncion': '☌', 'Quincuncio': '⚻',
            'Semisextil': '⚺', 'Sesquicuadratura': '⚼'
        }

    def select_csv_file(self) -> Optional[str]:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de eventos astrológicos",
            filetypes=[("Archivos CSV", "*.csv")],
            initialdir="."
        )
        return file_path

    def format_description(self, tipo_evento: str, descripcion: str) -> str:
        resultado = descripcion
        
        # Reemplazar nombres de planetas con sus símbolos
        for planeta, simbolo in self.simbolos.items():
            if planeta in resultado:
                if "ingresa" in resultado:
                    resultado = resultado.replace(
                        f"{planeta} ingresa",
                        f"{planeta} ({simbolo}) ingresa"
                    )
                elif " en " in resultado:
                    resultado = resultado.replace(
                        f"{planeta} en",
                        f"{planeta} ({simbolo}) en"
                    )
        
        # Reemplazar nombres de aspectos con sus símbolos
        for aspecto, simbolo in self.simbolos.items():
            if f" en {aspecto} " in resultado:
                resultado = resultado.replace(
                    f" en {aspecto} ",
                    f" en {aspecto} ({simbolo}) "
                )
        
        # Reemplazar nombres de signos con sus símbolos
        for signo, simbolo in self.simbolos.items():
            if f"de {signo}" in resultado:
                resultado = resultado.replace(
                    f"de {signo}",
                    f"de {signo} ({simbolo})"
                )
        
        return resultado

    def convert_csv_to_ics(self) -> None:
        self.logger.info("Iniciando proceso de conversión...")
        
        try:
            csv_path = self.select_csv_file()
            if not csv_path:
                self.logger.info("Proceso cancelado: No se seleccionó archivo")
                return
            
            # Crear calendario
            cal = Calendar()
            cal.add('prodid', '-//Eventos Astrológicos//ES')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            
            # Procesar eventos
            eventos_procesados = 0
            
            with open(csv_path, 'r', encoding='utf-8-sig') as file:  # Nota el cambio a utf-8-sig
                # Leer la primera línea para obtener los nombres de las columnas
                primera_linea = file.readline().strip()
                nombres_columnas = [col.strip() for col in primera_linea.split(',')]
                
                # Volver al inicio del archivo
                file.seek(0)
                
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Crear fecha y hora UTC
                        fecha_hora = datetime.strptime(
                            f"{row['Fecha UTC'].strip()} {row['Hora UTC'].strip()}", 
                            "%Y-%m-%d %H:%M"
                        ).replace(tzinfo=timezone.utc)
                        
                        # Crear evento iCal
                        ical_evento = Event()
                        descripcion = self.format_description(
                            row['Tipo de Evento'].strip(),
                            row['Descripción del Evento'].strip()
                        )
                        
                        titulo = f"{row['Tipo de Evento'].strip()}: {descripcion}"
                        contenido = (
                            f"Interpretación Personal:\n{row['Explicación Personal'].strip()}\n\n"
                            f"Interpretación Mundana:\n{row['Explicación Mundana'].strip()}"
                        )
                        
                        ical_evento.add('summary', titulo)
                        ical_evento.add('dtstart', fecha_hora)
                        ical_evento.add('description', contenido)
                        ical_evento['uid'] = f"{fecha_hora.strftime('%Y%m%d%H%M%S')}@astro"
                        
                        cal.add_component(ical_evento)
                        eventos_procesados += 1
                        
                    except KeyError as e:
                        self.logger.error(f"Error en el formato de la fila: {e}")
                        raise ValueError(f"El archivo CSV no contiene la columna necesaria: {e}")
                    except ValueError as e:
                        self.logger.error(f"Error en el formato de fecha/hora: {e}")
                        raise ValueError(f"Error en el formato de fecha/hora: {e}")
            
            # Guardar archivo ICS
            output_file = Path(csv_path).with_suffix('.ics')
            with open(output_file, 'wb') as f:
                f.write(cal.to_ical())
            
            mensaje_exito = (
                f"Conversión exitosa:\n"
                f"- Eventos procesados: {eventos_procesados}\n"
                f"- Archivo generado: {output_file}"
            )
            self.logger.info(mensaje_exito)
            messagebox.showinfo("Éxito", mensaje_exito)
            
        except Exception as e:
            error_msg = f"Error durante la conversión: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

def main():
    converter = AstroCalendarConverter()
    converter.convert_csv_to_ics()

if __name__ == "__main__":
    main()