from datetime import datetime
import pytz
from src.calculators.retrogrades import RetrogradeCalculator

def test_retrogrades_2025():
    # Datos esperados de Astroseek para 2025
    expected_stations = [
        ("Urano", "termina", "2025-01-30 13:22", "23°15' Tauro"),
        ("Júpiter", "termina", "2025-02-04 06:40", "11°16' Géminis"),
        ("Marte", "termina", "2025-02-23 23:00", "17°00' Cáncer"),
        ("Venus", "inicia", "2025-03-01 21:36", "10°50' Aries"),
        ("Mercurio", "inicia", "2025-03-15 03:46", "9°35' Aries"),
        ("Mercurio", "termina", "2025-04-07 08:08", "26°49' Piscis"),
        ("Venus", "termina", "2025-04-12 22:02", "24°37' Piscis"),
        ("Plutón", "inicia", "2025-05-04 12:27", "3°49' Acuario"),
        ("Neptuno", "inicia", "2025-07-04 18:33", "2°10' Aries"),
        ("Saturno", "inicia", "2025-07-13 01:07", "1°56' Aries"),
        ("Mercurio", "inicia", "2025-07-18 01:45", "15°34' Leo"),
        ("Mercurio", "termina", "2025-08-11 04:30", "4°14' Leo"),
        ("Urano", "inicia", "2025-09-06 01:51", "1°27' Géminis"),
        ("Plutón", "termina", "2025-10-13 23:52", "1°22' Acuario"),
        ("Mercurio", "inicia", "2025-11-09 16:01", "6°51' Sagitario"),
        ("Júpiter", "inicia", "2025-11-11 13:41", "25°09' Cáncer"),
        ("Saturno", "termina", "2025-11-28 00:51", "25°09' Piscis"),
        ("Mercurio", "termina", "2025-11-29 14:38", "20°42' Escorpio"),
        ("Neptuno", "termina", "2025-12-10 09:23", "29°22' Piscis")
    ]

    # Crear calculador
    calculator = RetrogradeCalculator()
    
    # Definir período de prueba (todo 2025)
    start_date = datetime(2025, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime(2026, 1, 1, tzinfo=pytz.UTC)
    
    # Calcular eventos
    calculated_events = calculator.calculate_retrogrades(start_date, end_date)
    
    print("\nComparación de estaciones planetarias 2025")
    print("=" * 120)
    print(f"{'Planeta':<10} {'Evento':<10} {'Fecha Esperada':<20} {'Fecha Calculada':<20} {'Dif (min)':<10} {'Posición esperada':<20} {'Posición calc.':<20} {'Match'}")
    print("-" * 120)

    # Para contar aciertos
    total_events = 0
    matched_events = 0
    missing_events = set(range(len(expected_stations)))

    # Comparar resultados
    for i, event in enumerate(calculated_events):
        total_events += 1
        match_found = False
        
        for j, expected in enumerate(expected_stations):
            planet, action, expected_date, expected_pos = expected
            if planet in event.descripcion and action in event.descripcion:
                missing_events.discard(j)
                match_found = True
                expected_dt = datetime.strptime(expected_date, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.UTC)
                calculated_dt = event.fecha_utc
                
                # Calcular diferencia en minutos
                diff = abs(calculated_dt - expected_dt)
                diff_minutes = diff.total_seconds() / 60
                
                # Extraer posición calculada
                calculated_pos = event.descripcion.split(" en ")[1]
                
                # Verificar coincidencia
                time_match = diff_minutes <= 5  # Tolerancia de 5 minutos
                pos_match = expected_pos in calculated_pos
                match = "✓" if time_match and pos_match else "✗"
                if time_match and pos_match:
                    matched_events += 1
                
                print(f"{planet:<10} {action:<10} {expected_date:<20} "
                      f"{calculated_dt.strftime('%Y-%m-%d %H:%M'):<20} "
                      f"{diff_minutes:>8.1f} {expected_pos:<20} {calculated_pos:<20} {match}")
                break
        
        if not match_found:
            print(f"{'EXTRA':<10} {'N/A':<10} {'N/A':<20} "
                  f"{event.fecha_utc.strftime('%Y-%m-%d %H:%M'):<20} "
                  f"{'N/A':>8} {'N/A':<20} {event.descripcion:<20} ✗")

    # Mostrar eventos faltantes
    if missing_events:
        print("\nEventos no encontrados:")
        for i in missing_events:
            planet, action, date, pos = expected_stations[i]
            print(f"- {planet} {action} {date} en {pos}")

    # Mostrar resumen
    print("\nResumen:")
    print(f"Total eventos esperados: {len(expected_stations)}")
    print(f"Total eventos calculados: {total_events}")
    print(f"Eventos correctos: {matched_events}")
    accuracy = (matched_events / len(expected_stations)) * 100 if len(expected_stations) > 0 else 0
    print(f"Precisión: {accuracy:.1f}%")

if __name__ == "__main__":
    try:
        print("Iniciando prueba de cálculo de retrogradaciones...")
        test_retrogrades_2025()
        print("\nPrueba completada.")
    except Exception as e:
        print(f"\nError durante la prueba: {e}")
        import traceback
        traceback.print_exc()