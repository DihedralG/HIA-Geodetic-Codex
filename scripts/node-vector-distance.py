from math import radians, cos, sin, asin, sqrt
import pandas as pd
import ace_tools as tools

# Define Haversine function
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3958.8  # Radius of Earth in miles
    return c * r

# Node coordinates
codex_nodes = {
    "Meadow House Observatory (MHO)": (44.397, -72.66),
    "Sayacmarca Observatory (SO)": (-13.17, -72.55),
    "Monte Verde Observatory (MVO)": (-39.316, -73.221),
    "Ciudad Perdida (CP01)": (11.0417, -73.9208),
    "Chiribiquete (Patio Bonito)": (0.719, -72.45)  # New node A41
}

# Calculate distances
chiribiquete_lat, chiribiquete_lon = codex_nodes["Chiribiquete (Patio Bonito)"]
distances = {
    name: round(haversine(chiribiquete_lon, chiribiquete_lat, lon, lat), 2)
    for name, (lat, lon) in codex_nodes.items()
    if name != "Chiribiquete (Patio Bonito)"
}

# Display
df = pd.DataFrame(distances.items(), columns=["Node", "Distance from Chiribiquete (mi)"])
tools.display_dataframe_to_user(name="Codex Node Distances from Chiribiquete", dataframe=df)