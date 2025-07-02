import matplotlib.pyplot as plt
!pip install cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

# Monte Carlo simulated sites (adjust as needed)
np.random.seed(42)
monte_carlo_longitudes = np.random.uniform(-180, 180, 400)
monte_carlo_latitudes = np.random.uniform(-60, 60, 400)

# Key nodes (adjust as needed)
nodes = {
    "Meadow House Observatory,(MHO) VerdeMont USA": (-72.66, 44.5),
    "Monte Verde Observatory, (MVO) Chili": (-73.2, -44.5),
    "Ciudad Perdida, Columbia": (-73.5, 11.2),
    "Laferriere Citadel, Haiti": (-72.8, 18.5),
    "Sayacmarca, Machu Pichu, Peru": (-72.5, -13.2),
    "Laschamp VGP Excursion": (2.5, 45),
    "Mono Lake VGP Excursion": (-119, 38),
    "North Atlantic Marker": (-40, 45),
    "South Atlantic Marker": (-20, -40),
    "Adams Calendar Megalithic Observatory, Mpumalanga, South Africa": (30, -25),
    "Monte Verde II occupation layer (~14,500 years ago)": (-73.2, -41.5),
    "Juukan Gorge": (120.88, -21.5554)
}

# Set up the Cartopy globe with orthographic projection
fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.Orthographic(central_longitude=-60, central_latitude=0))
ax.add_feature(cfeature.LAND, zorder=0, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, zorder=0, facecolor='white')
ax.add_feature(cfeature.COASTLINE, zorder=1)
ax.gridlines(draw_labels=False, linewidth=0.5, linestyle='--')


# Plot Monte Carlo sites
ax.scatter(monte_carlo_longitudes, monte_carlo_latitudes, color='gray', s=10,
           transform=ccrs.PlateCarree(), label='Monte Carlo Sites')


# Plot key nodes
for label, (lon, lat) in nodes.items():
    marker = 'X' if 'Laschamp' in label or 'Mono Lake' in label or 'Atlantic' in label else 'o'
    ax.scatter(lon, lat, s=100, marker=marker, transform=ccrs.PlateCarree(),
               label=label)


# Plot 72.66°W Corridor
ax.plot([-72.66, -72.66], [-90, 90], color='red', linewidth=2, linestyle='--',
        transform=ccrs.Geodetic(), label='72.66°W Corridor')

# Plot Tropics
tropic_cancer = 23.4367
tropic_capricorn = -23.4367
ax.plot([-180, 180], [tropic_cancer, tropic_cancer], color='orange', linestyle='--',
        transform=ccrs.Geodetic(), label='Tropic of Cancer')
ax.plot([-180, 180], [tropic_capricorn, tropic_capricorn], color='orange', linestyle='--',
        transform=ccrs.Geodetic(), label='Tropic of Capricorn')

# Optional: Add Equator
ax.plot([-180, 180], [0, 0], color='green', linestyle='--',
        transform=ccrs.Geodetic(), label='Equator')

# Optional: Add legend
ax.legend(loc='lower left', fontsize='small')

# Title
plt.title('Figure 21: Integrated Harmonic Geodetic Framework')

# Show plot
plt.show()