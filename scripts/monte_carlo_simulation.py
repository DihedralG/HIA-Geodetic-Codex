vprint('Monte Carlo Simulation Running')
import os

# Ensure 'data' directory exists before writing
if not os.path.exists("data"):
    os.makedirs("data")

# Now proceed with saving the results
output_path = "./HIA-Geodetic-Codex/data/mc_simulation_results.csv"
results_df.to_csv(output_path, index=False)

print(f"Monte Carlo simulation results saved to {output_path}")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load site coordinate data
site_data = pd.read_csv("./HIA-Geodetic-Codex/data/site_coordinates.csv")

# Define Monte Carlo parameters
num_simulations = 1000  # Number of randomized site distributions
lat_min, lat_max = site_data["Latitude"].min(), site_data["Latitude"].max()
lon_min, lon_max = site_data["Longitude"].min(), site_data["Longitude"].max()

# Store results
alignment_counts = []

# Monte Carlo Simulation
for _ in range(num_simulations):
    random_sites = pd.DataFrame({
        "Latitude": np.random.uniform(lat_min, lat_max, len(site_data)),
        "Longitude": np.random.uniform(lon_min, lon_max, len(site_data))
    })
    
    # Calculate the number of "alignments" (for demonstration, use a simple distance threshold)
    distances = np.sqrt((site_data["Latitude"] - random_sites["Latitude"])**2 + 
                        (site_data["Longitude"] - random_sites["Longitude"])**2)
    
    aligned_sites = np.sum(distances < 1.0)  # Example threshold of 1 degree
    alignment_counts.append(aligned_sites)


# Convert results to DataFrame
results_df = pd.DataFrame(alignment_counts, columns=["Number_of_Alignments"])

# Save results as CSV inside the repository
output_path = "./HIA-Geodetic-Codex/data/mc_simulation_results.csv"
results_df.to_csv(output_path, index=False)
print("Attempting to save Monte Carlo simulation results...")
# Plot histogram
plt.hist(alignment_counts, bins=50, color="blue", alpha=0.6, label="Monte Carlo Alignments")
plt.axvline(len(site_data), color="red", linestyle="dashed", label="Observed Alignments")
plt.xlabel("Number of Alignments")
plt.ylabel("Frequency")
plt.title("Monte Carlo Simulation of Site Alignments")
plt.legend()
plt.show()

# Compute significance
p_value = np.sum(np.array(alignment_counts) >= len(site_data)) / num_simulations
print(f"P-value of observed alignment: {p_value:.5f}")

print(f"Monte Carlo simulation results saved to {output_path}")







