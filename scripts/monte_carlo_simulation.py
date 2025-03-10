import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print("Monte Carlo Simulation Running")

# Define paths
repo_root = os.getcwd()  # Get working directory
data_dir = os.path.join(repo_root, "HIA-Geodetic-Codex/data")
output_path = os.path.join(data_dir, "mc_simulation_results.csv")

# Ensure data directory exists
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Created directory: {data_dir}")
else:
    print(f"Directory already exists: {data_dir}")

# Load site coordinate data
site_data_path = os.path.join(data_dir, "site_coordinates.csv")
if not os.path.exists(site_data_path):
    print(f"Error: site_coordinates.csv not found at {site_data_path}")
    exit()

site_data = pd.read_csv(site_data_path)

# Define Monte Carlo parameters
num_simulations = 1000  # Reduced from 10,000 for testing
lat_min, lat_max = site_data["Latitude"].min(), site_data["Latitude"].max()
lon_min, lon_max = site_data["Longitude"].min(), site_data["Longitude"].max()

# Store results
alignment_counts = []

# Monte Carlo Simulation Loop
for i in range(num_simulations):
    random_sites = pd.DataFrame({
        "Latitude": np.random.uniform(lat_min, lat_max, len(site_data)),
        "Longitude": np.random.uniform(lon_min, lon_max, len(site_data))
    })

    # Calculate distances
    distances = np.sqrt(
        (site_data["Latitude"] - random_sites["Latitude"])**2 +
        (site_data["Longitude"] - random_sites["Longitude"])**2
    )

    # Count alignments within 1-degree threshold
    aligned_sites = np.sum(distances < 1.0)  # Adjust this threshold if needed

    # Debugging: Print alignment counts per iteration
    if i % 100 == 0:  # Print every 100 iterations
        print(f"Simulation {i}: {aligned_sites} alignments")

    alignment_counts.append(aligned_sites)  # Append to list

# Check if alignment_counts is populated
if not alignment_counts:
    print("Error: No alignment counts were generated.")
    exit()

# Convert results to DataFrame
results_df = pd.DataFrame(alignment_counts, columns=["Number_of_Alignments"])

# Save results to CSV inside the repository
results_df.to_csv(output_path, index=False)
print(f"Monte Carlo simulation results saved to {output_path}")

# Verify the file was created
if os.path.exists(output_path):
    print("Monte Carlo simulation results successfully saved.")
else:
    print("Error: File was not created.")

# Plot histogram
plt.hist(alignment_counts, bins=50, color="blue", alpha=0.6, label="Monte Carlo Alignments")
plt.axvline(len(site_data), color="red", linestyle="dashed", label="Observed Alignments")
plt.xlabel("Number of Alignments")
plt.ylabel("Frequency")
plt.title("Monte Carlo Simulation of Site Alignments")
plt.legend()
plt.show()

# Compute statistical significance
p_value = np.sum(np.array(alignment_counts) >= len(site_data)) / num_simulations
print(f"p-value of observed alignment: {p_value:.5f}")

print("Monte Carlo simulation completed successfully.")