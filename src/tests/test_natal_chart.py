import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from ..calculators.natal_chart import NatalChart, calcular_carta_natal
from ..core.location import Location

@pytest.fixture
def test_location():
    """Fixture que proporciona una ubicación de prueba (Buenos Aires)."""
    return Location(
        lat=-34.6037,
        lon=-58.3816,
        name="Buenos Aires",
        timezone="America/Argentina/Buenos_Aires"
    )

@pytest.fixture
def test_time():
    """Fixture que proporciona una fecha/hora de prueba."""
    return datetime(2000, 1, 1, 12, 0, tzinfo=ZoneInfo('UTC'))

def test_natal_chart_creation(test_location, test_time):
    """Prueba la creación básica de una carta natal."""
    chart = NatalChart(test_time, test_location)
    assert chart is not None
    assert hasattr(chart, 'positions')
    assert hasattr(chart, 'angles')

def test_planet_positions(test_location, test_time):
    """Prueba el cálculo de posiciones planetarias."""
    chart = NatalChart(test_time, test_location)
    
    # Verificar que todos los planetas estén calculados
    expected_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                       'Saturn', 'Uranus', 'Neptune', 'Pluto']
    
    for planet in expected_planets:
        assert planet in chart.positions
        position = chart.positions[planet]
        
        # Verificar estructura de datos
        assert 'longitude' in position
        assert 'sign' in position
        assert 'degrees_in_sign' in position
        
        # Verificar rangos válidos
        assert 0 <= position['longitude'] < 360
        assert 0 <= position['degrees_in_sign'] < 30
        assert position['sign'] in ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 
                                  'Virgo', 'Libra', 'Escorpio', 'Sagitario', 
                                  'Capricornio', 'Acuario', 'Piscis']

def test_angles_calculation(test_location, test_time):
    """Prueba el cálculo de ángulos principales."""
    chart = NatalChart(test_time, test_location)
    
    # Verificar que todos los ángulos estén presentes
    expected_angles = ['ASC', 'MC', 'DSC', 'IC']
    
    for angle in expected_angles:
        assert angle in chart.angles
        assert 'longitude' in chart.angles[angle]
        assert 'label' in chart.angles[angle]
        
        # Verificar rangos válidos
        assert 0 <= chart.angles[angle]['longitude'] < 360
        
    # Verificar relaciones entre ángulos
    assert abs((chart.angles['DSC']['longitude'] - chart.angles['ASC']['longitude']) % 360 - 180) < 0.1
    assert abs((chart.angles['IC']['longitude'] - chart.angles['MC']['longitude']) % 360 - 180) < 0.1

def test_houses_calculation(test_location, test_time):
    """Prueba el cálculo de casas."""
    chart = NatalChart(test_time, test_location)
    chart._calculate_houses()
    
    # Verificar que todas las casas estén presentes
    for house_num in range(1, 13):
        assert house_num in chart.houses
        house = chart.houses[house_num]
        
        # Verificar estructura de datos
        assert 'start' in house
        assert 'end' in house
        assert 'system' in house
        
        # Verificar rangos válidos
        assert 0 <= house['start'] < 360
        assert 0 <= house['end'] < 360

def test_chart_to_dict(test_location, test_time):
    """Prueba la conversión de la carta a diccionario."""
    chart = NatalChart(test_time, test_location)
    data = chart.to_dict()
    
    # Verificar estructura del diccionario
    assert 'birth_time' in data
    assert 'location' in data
    assert 'planets' in data
    assert 'angles' in data
    assert 'houses' in data
    
    # Verificar datos de ubicación
    assert data['location']['latitude'] == test_location.lat
    assert data['location']['longitude'] == test_location.lon
    assert data['location']['timezone'] == test_location.timezone

def test_calcular_carta_natal():
    """Prueba la función principal de cálculo de carta natal."""
    datos_usuario = {
        "hora_utc": "2000-01-01T12:00:00",
        "lat": -34.6037,
        "lon": -58.3816,
        "zona_horaria": "America/Argentina/Buenos_Aires",
        "lugar": "Buenos Aires"
    }
    
    resultado = calcular_carta_natal(datos_usuario)
    assert resultado is not None
    assert 'planets' in resultado
    assert 'angles' in resultado
    assert 'houses' in resultado

def test_error_handling():
    """Prueba el manejo de errores."""
    # Datos inválidos
    datos_invalidos = {
        "hora_utc": "fecha_invalida",
        "lat": -34.6037,
        "lon": -58.3816,
        "zona_horaria": "America/Argentina/Buenos_Aires"
    }
    
    with pytest.raises(ValueError):
        calcular_carta_natal(datos_invalidos)
    
    # Datos incompletos
    datos_incompletos = {
        "hora_utc": "2000-01-01T12:00:00"
        # Faltan lat y lon
    }
    
    with pytest.raises(KeyError):
        calcular_carta_natal(datos_incompletos)
