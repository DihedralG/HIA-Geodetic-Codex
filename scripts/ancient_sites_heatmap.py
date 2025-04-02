import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic

def plot_heatmap(data):
    plt.figure(figsize=(15, 7))
    sns.kdeplot(x=data['Longitude'], y=data['Latitude'], fill=True, cmap='viridis', bw_adjust=0.5)
    plt.scatter(data['Longitude'], data['Latitude'], color='white', edgecolor='black', s=50)
    plt.title("Ancient Sites Harmonic Intelligence Heatmap")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.show()
