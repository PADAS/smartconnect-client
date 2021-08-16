import pytz

import json
import statistics, timezonefinder
from datetime import timezone, tzinfo

from smartconnect import models

def guess_ca_timezone(ca:models.ConservationArea) -> tzinfo:
    '''
    Guess the timezone based on boundary.
    This naively uses the average longitude and latitude values from the boundary's 
    multipolygon. An improvment might be to calculate a centroid, or better yet to
    find all intersected timezones and pick the most prominent one.
    '''
    boundary = json.loads(ca.caBoundaryJson)

    accum = []
    for geometry in boundary['geometries']:
        if geometry['type'] == 'MultiPolygon':
            accum.extend(geometry['coordinates'][0][0])

    avg_longitude = statistics.mean([x[0] for x in accum])
    avg_latitude = statistics.mean([x[1] for x in accum])

    print(f'Average: {avg_longitude}, {avg_latitude}')

    predicted_timezone = timezonefinder.TimezoneFinder().timezone_at(lng=avg_longitude, lat=avg_latitude)        
    return pytz.timezone(predicted_timezone)