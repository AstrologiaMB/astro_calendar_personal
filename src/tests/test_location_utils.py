import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from geopy.exc import GeocoderTimedOut
from geopy.location import Location as GeopyLocation
from ..utils.location_utils import (
    get_coordinates,
    get_timezone,
    create_location_from_place,
    local_to_utc,
    utc_to_local
)
from ..core.location import Location

def test_get_coordinates():
    # Test with a well-known location
    lat, lon, elevation = get_coordinates("Buenos Aires, Argentina", timeout=30)
    assert -35.0 < lat < -34.0  # Buenos Aires latitude range
    assert -59.0 < lon < -58.0  # Buenos Aires longitude range
    assert isinstance(elevation, (int, float))

    # Test with invalid location
    with pytest.raises(ValueError):
        get_coordinates("ThisPlaceDoesNotExist12345")

def test_get_timezone():
    # Test Buenos Aires coordinates
    timezone = get_timezone(-34.6037, -58.3816)
    assert timezone == "America/Argentina/Buenos_Aires"

    # Test coordinates in the middle of Pacific Ocean
    timezone = get_timezone(-45.0, -150.0)
    assert timezone.startswith("Etc/GMT")  # Ocean timezones use Etc/GMT format

def test_create_location_from_place():
    # Test creating location for Buenos Aires
    location = create_location_from_place("Buenos Aires, Argentina")
    assert isinstance(location, Location)
    assert -35.0 < location.lat < -34.0
    assert -59.0 < location.lon < -58.0
    assert location.timezone == "America/Argentina/Buenos_Aires"

def test_time_conversions():
    # Test UTC to local time conversion
    utc_time = datetime(2024, 1, 1, 12, 0, tzinfo=ZoneInfo('UTC'))
    local_time = utc_to_local(utc_time, "America/Argentina/Buenos_Aires")
    assert local_time.hour == 9  # Buenos Aires is UTC-3

    # Test local time to UTC conversion
    local_time = datetime(2024, 1, 1, 9, 0)
    utc_time = local_to_utc(local_time, "America/Argentina/Buenos_Aires")
    assert utc_time.hour == 12  # Converting back to UTC

def test_get_coordinates_retry(monkeypatch):
    attempts = 0
    
    class MockLocation:
        def __init__(self):
            self.latitude = -34.6037
            self.longitude = -58.3816
            self.altitude = 0
    
    def mock_geocode(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise GeocoderTimedOut()
        return MockLocation()
    
    # Create a mock geocoder object
    class MockGeocoder:
        def geocode(self, *args, **kwargs):
            return mock_geocode(*args, **kwargs)
    
    # Patch the module-level geocoder
    import src.utils.location_utils as location_utils
    monkeypatch.setattr(location_utils, "geocoder", MockGeocoder())
    
    # Should succeed after retries
    lat, lon, elevation = get_coordinates("Test Location", max_retries=3)
    assert lat == -34.6037
    assert lon == -58.3816
    assert elevation == 0
    assert attempts == 3  # Verify it took exactly 3 attempts
    
    # Reset attempts counter
    attempts = 0
    
    # Test that it fails after max retries
    with pytest.raises(ValueError, match=".*timed out.*"):
        get_coordinates("Test Location", max_retries=1, timeout=1)
