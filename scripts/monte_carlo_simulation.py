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
num_simulations = 10000  # Reduced from 10,000 for testing
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

    # Debugging: Print random sites sample
    if i == 0:
        print("Random sites sample:")
        print(random_sites.head())

    # Calculate distances
    distances = np.sqrt(
        (site_data["Latitude"].values - random_sites["Latitude"].values) ** 2 +
        (site_data["Longitude"].values - random_sites["Longitude"].values) ** 2
    )

    # Count alignments within 1-degree threshold
    aligned_sites = np.sum(distances < 1.0)  # Adjust threshold if needed

    # Debugging: Print distance sample and aligned count
    if i % 100 == 0:
        print(f"Simulation {i}: {aligned_sites} alignments found")

    alignment_counts.append(aligned_sites)

# Debugging: Print sample alignment counts
print("Alignment counts sample:", alignment_counts[:10])

# Check if alignment_counts is populated
if not alignment_counts or sum(alignment_counts) == 0:
    print("❌ Error: No alignments detected. Check input data.")
    exit()

# Convert results to DataFrame
results_df = pd.DataFrame(alignment_counts, columns=["Number_of_Alignments"])

# Debugging: Show DataFrame before saving
print("Monte Carlo results DataFrame preview:")
print(results_df.head())

# Check if DataFrame has data before saving
if results_df.empty:
    print("❌ Error: DataFrame is empty, nothing to save.")
else:
    results_df.to_csv(output_path, index=False)
    print(f"✅ Monte Carlo simulation results saved to {output_path}")

# Verify the file was created and contains data
if os.path.exists(output_path):
    df_check = pd.read_csv(output_path)
    if df_check.empty:
        print("❌ Error: The saved CSV file is empty!")
    else:
        print("✅ Saved CSV file contains data!")
else:
    print("❌ Error: The file was not created.")

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