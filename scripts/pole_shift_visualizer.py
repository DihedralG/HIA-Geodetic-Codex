import matplotlib.pyplot as plt

def plot_pole_shifts(pole_data, site_data):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(pole_data['Longitude'], pole_data['Latitude'], 'r--', label='Pole Shift Trajectory')
    ax.scatter(site_data['Longitude'], site_data['Latitude'], c='blue', label='Ancient Sites', alpha=0.6)
    ax.set_title("Pole Shift Trajectory & Ancient Site Overlay")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    plt.grid(True)
    plt.show()
