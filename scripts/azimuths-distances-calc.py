from geopy.distance import geodesic
from math import atan2, degrees, radians, sin, cos

# Define coordinates
meadow_house = (44.4300, -72.6600)         # Approximate Meadow House Observatory (Vermont)
patio_bonito = (1.1600, -72.6600)          # Patio Bonito / CO41 (Equatorial Zone)
co42 = (10.4219, -72.6620)                 # Trihedral Basin Site / CO42
monte_verde = (-39.3172, -73.2265)         # Monte Verde region (Chile)

# Function to calculate azimuth (initial bearing)
def calculate_azimuth(coord1, coord2):
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(dlon)
    initial_bearing = atan2(x, y)
    return (degrees(initial_bearing) + 360) % 360

# Calculate azimuths and distances
azimuth_MHO_to_PB = calculate_azimuth(meadow_house, patio_bonito)
distance_MHO_to_PB = geodesic(meadow_house, patio_bonito).miles

azimuth_MVO_to_MHO = calculate_azimuth(monte_verde, meadow_house)
distance_MVO_to_MHO = geodesic(monte_verde, meadow_house).miles

azimuth_MHO_to_CO42 = calculate_azimuth(meadow_house, co42)
distance_MHO_to_CO42 = geodesic(meadow_house, co42).miles

azimuth_PB_to_CO42 = calculate_azimuth(patio_bonito, co42)
distance_PB_to_CO42 = geodesic(patio_bonito, co42).miles

{
    "azimuth_MHO_to_PB": azimuth_MHO_to_PB,
    "distance_MHO_to_PB": distance_MHO_to_PB,
    "azimuth_MVO_to_MHO": azimuth_MVO_to_MHO,
    "distance_MVO_to_MHO": distance_MVO_to_MHO,
    "azimuth_MHO_to_CO42": azimuth_MHO_to_CO42,
    "distance_MHO_to_CO42": distance_MHO_to_CO42,
    "azimuth_PB_to_CO42": azimuth_PB_to_CO42,
    "distance_PB_to_CO42": distance_PB_to_CO42,
}