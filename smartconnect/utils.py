import pytz
import shapely

import timezonefinder
from datetime import tzinfo

from smartconnect import models

def guess_ca_timezone(ca:models.ConservationArea) -> tzinfo:
    '''
    Guess the timezone based on boundary included with the conservation area metadata.

    Args: a ConservationArea 
    Returns: a tzinfo object representing the timezone for the center of the conservation area, or None
    References: https://pypi.org/project/timezonefinder/

    The ConservationArea object has a field called caBoundaryJson which is string holding a GeoJSON object.
    '''

    if not ca or not ca.caBoundaryJson:
        return 
    
    boundary = shapely.from_geojson(ca.caBoundaryJson, on_invalid='warn')

    if boundary:
        predicted_timezone = timezonefinder.TimezoneFinder().timezone_at(lng=boundary.centroid.x, lat=boundary.centroid.y)        
        return pytz.timezone(predicted_timezone)

