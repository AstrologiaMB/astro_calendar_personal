from icalendar import Calendar, Event
import os

def validate_and_adjust_ics(input_file, output_file):
    try:
        # Leer el archivo .ics original
        with open(input_file, 'r', encoding='utf-8') as file:
            calendar = Calendar.from_ical(file.read())

        # Crear un nuevo calendario para la salida
        new_calendar = Calendar()
        new_calendar.add('prodid', '-//Google Calendar Compatibility//EN')
        new_calendar.add('version', '2.0')

        for component in calendar.walk():
            # Mantener solo los eventos
            if component.name == "VEVENT":
                new_event = Event()
                for key, value in component.items():
                    # Validar y copiar propiedades
                    new_event.add(key, value)
                # Copiar el contenido del evento
                for subcomponent in component.subcomponents:
                    new_event.add_component(subcomponent)
                new_calendar.add_component(new_event)

        # Guardar el archivo .ics compatible
        with open(output_file, 'wb') as file:
            file.write(new_calendar.to_ical())

        print(f"Archivo convertido con éxito: {output_file}")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

# Ruta del archivo original y del archivo ajustado
input_file = "Calendario_Astrologico_2025.ics"  # Cambia este nombre según el archivo
output_file = "Calendario_Astrologico_2025_compatible.ics"

# Ejecutar la función
validate_and_adjust_ics(input_file, output_file)