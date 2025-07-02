# Re-importing necessary libraries since the kernel was reset
import matplotlib.pyplot as plt
import numpy as np

# Monte Carlo simulated sites (random scatter around the globe for demonstration)
np.random.seed(42)
monte_carlo_longitudes = np.random.uniform(-180, 180, 400)
monte_carlo_latitudes = np.random.uniform(-60, 60, 400)

# 72.66°W corridor (vertical line)
corridor_longitude = -72.66


# Specific global nodes
nodes = {
    "Northern Magnetic Pole, (current)": (-72.66, 90.),
    "Undisclosed Canadian Location": (-72.66, 61),
    "Undisclosed, Greenland, (GO)": (-72.3, 76.4),
    "MHO": (-72.66, 44.5),
    "Ciudad Perdida (CPO), Colombia": (-73.55, 11.2),
    "Citadelle Laferrière (CLO), Haiti": (-72.2, 19.6),
    "Sayacmarca, Peru (SO)": (-73.5, -13.5),
     "Monte Verde, Chili (MVO)": (-73.2, -41.5),
    "Meadow House Inverse Fulcrum (MVO)": (-72.66, -44.3),
     "Southern Magnetic Pole (current)": (-72.66,-90),
    "Adams Calendar": (30, -25),
    "Drake's Passage": (-70, -60),
    "Vinson Massif": (-78.31, -85.37),
    "Juukan Gorge, Australia": (117.9, -22.37),
    "Laschamp": (2.5, 45),
    "Mono Lake": (-119, 38),
    "North Atlantic": (-40, 45),
    "South Atlantic": (-20, -40)

}

# Tropics
tropic_cancer = 23.4367
tropic_capricorn = -23.4367

# Plot setup
plt.figure(figsize=(14, 8))
plt.scatter(monte_carlo_longitudes, monte_carlo_latitudes, color='gray', s=10, label='Monte Carlo Sites')
plt.axvline(corridor_longitude, color='red', linestyle='--', linewidth=2, label='72.66°W Corridor')
plt.axhline(tropic_cancer, color='orange', linestyle='--', linewidth=1, label='Tropic of Cancer')
plt.axhline(tropic_capricorn, color='orange', linestyle='--', linewidth=1, label='Tropic of Capricorn')

# Plot nodes
for label, (lon, lat) in nodes.items():
    plt.scatter(lon, lat, s=100, marker='X' if 'Laschamp' in label or 'Mono Lake' in label or 'Atlantic' in label else 'o',
                label=label)

# Paleopole arcs (approximate examples)
arc_lats = [-80, -30, 0, 30, 80]
for lat in arc_lats:
    ax.plot(np.linspace(-180, 180, 200), [lat]*200, transform=ccrs.PlateCarree(),
            color='green', linestyle=':', alpha=0.5)

# Formatting
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Figure 21: Integrated Harmonic Geodetic Framework')
plt.xlim(-180, 180)
plt.ylim(-90, 90)
plt.grid(True, linestyle='--', linewidth=0.5)
plt.legend(loc='lower left', fontsize='small')

# Show plot
plt.show()