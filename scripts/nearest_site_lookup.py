import pandas as pd
from geopy.distance import geodesic

def find_nearest_site(lat, lon, data):
    user_coords = (lat, lon)
    data['Distance_km'] = data.apply(lambda row: geodesic(user_coords, (row['Latitude'], row['Longitude'])).km, axis=1)
    return data.sort_values('Distance_km').iloc[0]
