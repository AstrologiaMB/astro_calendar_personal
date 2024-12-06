"""
Tests para el módulo de análisis de eclipses.
"""
import unittest
from datetime import datetime
import pytz
from ..calculators.eclipse_analysis import EclipseAnalyzer, analizar_eclipses_periodo
from ..core.base_event import AstroEvent
from ..core.constants import EventType

class TestEclipseAnalysis(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para las pruebas."""
        # Carta natal de ejemplo con casas cada 30°
        self.natal_chart = {
            'planets': {
                'Sun': {'lon': '45.5', 'lat': '0.0', 'speed': '1.0'},
                'Moon': {'lon': '120.3', 'lat': '0.0', 'speed': '13.0'},
                'North Node': {'lon': '75.0', 'lat': '0.0', 'speed': '0.0'},
            },
            'houses': {
                '1': '0.0',    # Casa 1 empieza en 0°
                '2': '30.0',   # Casa 2 empieza en 30°
                '3': '60.0',   # Casa 3 empieza en 60°
                '4': '90.0',   # Casa 4 empieza en 90°
                '5': '120.0',  # Casa 5 empieza en 120°
                '6': '150.0',  # Casa 6 empieza en 150°
                '7': '180.0',  # Casa 7 empieza en 180°
                '8': '210.0',  # Casa 8 empieza en 210°
                '9': '240.0',  # Casa 9 empieza en 240°
                '10': '270.0', # Casa 10 empieza en 270°
                '11': '300.0', # Casa 11 empieza en 300°
                '12': '330.0'  # Casa 12 empieza en 330°
            }
        }
        
        # Eclipse de ejemplo en 45° (debería estar en la segunda casa: 30°-60°)
        self.sample_eclipse = AstroEvent(
            fecha_utc=datetime(2024, 4, 8, 18, 20, tzinfo=pytz.UTC),
            tipo_evento=EventType.ECLIPSE_SOLAR,
            descripcion="Eclipse Solar Total",
            elevacion=45.0,
            azimut=180.0,
            longitud1=45.0,  # Posición a 45° (entre 30° y 60°)
            signo="Tauro",
            grado=15.0
        )
        
        self.analyzer = EclipseAnalyzer(self.natal_chart)

    def test_house_activation(self):
        """Prueba la determinación de la casa activada por el eclipse."""
        impact = self.analyzer.analyze_eclipse_impact(self.sample_eclipse)
        
        # Debug: Imprimir información relevante
        print(f"\nEclipse longitud: {self.sample_eclipse.longitud1}°")
        print("Casas:")
        for i in range(1, 13):
            print(f"Casa {i}: {self.natal_chart['houses'][str(i)]}°")
        print(f"Casa activada según cálculo: {impact['casa_activada']['numero']}")
        
        # El eclipse está en 45° que debería caer en la segunda casa (entre 30° y 60°)
        self.assertEqual(impact['casa_activada']['numero'], 2)
        self.assertEqual(impact['casa_activada']['cuspide'], 30.0)
        self.assertEqual(impact['casa_activada']['siguiente_cuspide'], 60.0)

    def test_aspect_analysis(self):
        """Prueba el análisis de aspectos con planetas natales."""
        impact = self.analyzer.analyze_eclipse_impact(self.sample_eclipse)
        
        # Debería encontrar una conjunción con el Sol natal
        aspectos_sol = [asp for asp in impact['aspectos'] if asp['planeta'] == 'Sun']
        self.assertTrue(len(aspectos_sol) > 0)
        self.assertEqual(aspectos_sol[0]['tipo'], 'conjunction')
        self.assertLess(abs(aspectos_sol[0]['orbe']), 1.0)

    def test_node_relationship(self):
        """Prueba el análisis de la relación con los nodos lunares."""
        impact = self.analyzer.analyze_eclipse_impact(self.sample_eclipse)
        
        # El eclipse está a 30° del Nodo Norte
        self.assertLess(abs(impact['nodos']['distancia_nodo_norte'] - 30), 1.0)
        self.assertFalse(impact['nodos']['conjuncion_nodo'])

    def test_periodo_analysis(self):
        """Prueba el análisis de eclipses en un período."""
        start_date = datetime(2024, 1, 1, tzinfo=pytz.UTC)
        end_date = datetime(2024, 12, 31, tzinfo=pytz.UTC)
        location = {
            'latitude': -34.6037,
            'longitude': -58.3816
        }
        
        resultados = analizar_eclipses_periodo(
            self.natal_chart,
            start_date,
            end_date,
            location
        )
        
        # Verificar que se encontraron eclipses
        self.assertTrue(len(resultados) > 0)
        
        # Verificar estructura del resultado
        for resultado in resultados:
            self.assertIn('fecha_utc', resultado)
            self.assertIn('tipo', resultado)
            self.assertIn('posicion', resultado)
            self.assertIn('casa_activada', resultado)
            self.assertIn('aspectos', resultado)
            self.assertIn('nodos', resultado)

if __name__ == '__main__':
    unittest.main()
