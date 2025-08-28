import pytest
from unittest.mock import Mock, patch
import pytz
from datetime import tzinfo

from smartconnect import utils
from smartconnect.models import ConservationArea


class TestGuessCATimezone:
    """Test the guess_ca_timezone function."""
    
    def test_guess_ca_timezone_with_valid_boundary(self):
        """Test guessing timezone with valid boundary data."""
        # Mock ConservationArea with valid boundary
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = '''
        {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        }
        '''
        
        # Mock shapely and timezonefinder
        with patch('smartconnect.utils.shapely') as mock_shapely:
            with patch('smartconnect.utils.timezonefinder') as mock_timezonefinder:
                # Mock boundary object with centroid
                mock_boundary = Mock()
                mock_boundary.centroid.x = 0.5
                mock_boundary.centroid.y = 0.5
                mock_shapely.from_geojson.return_value = mock_boundary
                
                # Mock timezone finder
                mock_tf = Mock()
                mock_tf.timezone_at.return_value = "Africa/Nairobi"
                mock_timezonefinder.TimezoneFinder.return_value = mock_tf
                
                result = utils.guess_ca_timezone(ca)
                
                assert result == pytz.timezone("Africa/Nairobi")
                mock_shapely.from_geojson.assert_called_once_with(ca.caBoundaryJson, on_invalid='warn')
                mock_tf.timezone_at.assert_called_once_with(lng=0.5, lat=0.5)
    
    def test_guess_ca_timezone_with_none_ca(self):
        """Test guessing timezone with None conservation area."""
        result = utils.guess_ca_timezone(None)
        assert result is None
    
    def test_guess_ca_timezone_with_no_boundary(self):
        """Test guessing timezone with conservation area that has no boundary."""
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = None
        
        result = utils.guess_ca_timezone(ca)
        assert result is None
    
    def test_guess_ca_timezone_with_empty_boundary(self):
        """Test guessing timezone with empty boundary string."""
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = ""
        
        result = utils.guess_ca_timezone(ca)
        assert result is None
    
    def test_guess_ca_timezone_with_invalid_boundary(self):
        """Test guessing timezone with invalid boundary data."""
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = "invalid json"
        
        with patch('smartconnect.utils.shapely') as mock_shapely:
            # Mock shapely to return None for invalid data
            mock_shapely.from_geojson.return_value = None
            
            result = utils.guess_ca_timezone(ca)
            
            assert result is None
            mock_shapely.from_geojson.assert_called_once_with(ca.caBoundaryJson, on_invalid='warn')
    
    def test_guess_ca_timezone_with_timezone_finder_none(self):
        """Test guessing timezone when timezone finder returns None."""
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = '''
        {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        }
        '''
        
        with patch('smartconnect.utils.shapely') as mock_shapely:
            with patch('smartconnect.utils.timezonefinder') as mock_timezonefinder:
                # Mock boundary object with centroid
                mock_boundary = Mock()
                mock_boundary.centroid.x = 0.5
                mock_boundary.centroid.y = 0.5
                mock_shapely.from_geojson.return_value = mock_boundary
                
                # Mock timezone finder to return None
                mock_tf = Mock()
                mock_tf.timezone_at.return_value = None
                mock_timezonefinder.TimezoneFinder.return_value = mock_tf
                
                # The function should raise an exception when timezone is None
                with pytest.raises(pytz.exceptions.UnknownTimeZoneError):
                    utils.guess_ca_timezone(ca)
                
                mock_tf.timezone_at.assert_called_once_with(lng=0.5, lat=0.5)
    
    def test_guess_ca_timezone_with_invalid_timezone(self):
        """Test guessing timezone when timezone finder returns invalid timezone."""
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = '''
        {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        }
        '''
        
        with patch('smartconnect.utils.shapely') as mock_shapely:
            with patch('smartconnect.utils.timezonefinder') as mock_timezonefinder:
                with patch('smartconnect.utils.pytz') as mock_pytz:
                    # Mock boundary object with centroid
                    mock_boundary = Mock()
                    mock_boundary.centroid.x = 0.5
                    mock_boundary.centroid.y = 0.5
                    mock_shapely.from_geojson.return_value = mock_boundary
                    
                    # Mock timezone finder to return invalid timezone
                    mock_tf = Mock()
                    mock_tf.timezone_at.return_value = "Invalid/Timezone"
                    mock_timezonefinder.TimezoneFinder.return_value = mock_tf
                    
                    # Mock pytz to raise exception
                    mock_pytz.timezone.side_effect = pytz.exceptions.UnknownTimeZoneError("Invalid timezone")
                    
                    with pytest.raises(pytz.exceptions.UnknownTimeZoneError):
                        utils.guess_ca_timezone(ca)
    
    def test_guess_ca_timezone_with_real_coordinates(self):
        """Test guessing timezone with realistic coordinates."""
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = '''
        {
            "type": "Polygon",
            "coordinates": [[[36.8, -1.3], [36.9, -1.3], [36.9, -1.2], [36.8, -1.2], [36.8, -1.3]]]
        }
        '''
        
        with patch('smartconnect.utils.shapely') as mock_shapely:
            with patch('smartconnect.utils.timezonefinder') as mock_timezonefinder:
                # Mock boundary object with Nairobi coordinates
                mock_boundary = Mock()
                mock_boundary.centroid.x = 36.85  # Longitude
                mock_boundary.centroid.y = -1.25  # Latitude
                mock_shapely.from_geojson.return_value = mock_boundary
                
                # Mock timezone finder
                mock_tf = Mock()
                mock_tf.timezone_at.return_value = "Africa/Nairobi"
                mock_timezonefinder.TimezoneFinder.return_value = mock_tf
                
                result = utils.guess_ca_timezone(ca)
                
                assert result == pytz.timezone("Africa/Nairobi")
                mock_tf.timezone_at.assert_called_once_with(lng=36.85, lat=-1.25)
    
    def test_guess_ca_timezone_with_complex_boundary(self):
        """Test guessing timezone with complex boundary geometry."""
        ca = Mock(spec=ConservationArea)
        ca.caBoundaryJson = '''
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]]
            ]
        }
        '''
        
        with patch('smartconnect.utils.shapely') as mock_shapely:
            with patch('smartconnect.utils.timezonefinder') as mock_timezonefinder:
                # Mock boundary object with centroid
                mock_boundary = Mock()
                mock_boundary.centroid.x = 1.5
                mock_boundary.centroid.y = 1.5
                mock_shapely.from_geojson.return_value = mock_boundary
                
                # Mock timezone finder
                mock_tf = Mock()
                mock_tf.timezone_at.return_value = "Europe/London"
                mock_timezonefinder.TimezoneFinder.return_value = mock_tf
                
                result = utils.guess_ca_timezone(ca)
                
                assert result == pytz.timezone("Europe/London")
                mock_tf.timezone_at.assert_called_once_with(lng=1.5, lat=1.5)


class TestUtilsIntegration:
    """Integration tests for utils module."""
    
    def test_utils_module_imports(self):
        """Test that utils module can be imported and has expected functions."""
        assert hasattr(utils, 'guess_ca_timezone')
        assert callable(utils.guess_ca_timezone)
    
    def test_utils_function_signature(self):
        """Test that guess_ca_timezone has the expected signature."""
        import inspect
        
        sig = inspect.signature(utils.guess_ca_timezone)
        params = list(sig.parameters.keys())
        
        assert len(params) == 1
        assert params[0] == 'ca'
        
        # Check return type annotation
        assert sig.return_annotation == tzinfo
    
    def test_utils_docstring(self):
        """Test that guess_ca_timezone has proper documentation."""
        doc = utils.guess_ca_timezone.__doc__
        
        assert doc is not None
        assert "Guess the timezone" in doc
        assert "ConservationArea" in doc
        assert "tzinfo" in doc
        assert "timezonefinder" in doc