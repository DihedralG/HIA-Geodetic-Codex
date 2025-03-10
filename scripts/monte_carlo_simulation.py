import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

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
    print(f"❌ Error: site_coordinates.csv not found at {site_data_path}")
    exit()

site_data = pd.read_csv(site_data_path)
print(f"✅ Loaded site data with {len(site_data)} records.")

# Define Monte Carlo parameters
num_simulations = 10000  # Force to 10,000
print(f"✅ Running {num_simulations} simulations...")

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

    # Debugging: Print random sites sample for first iteration
    if i == 0:
        print("🟢 Random sites sample:")
        print(random_sites.head())

    # Calculate distances
    distances = np.sqrt(
        (site_data["Latitude"].values - random_sites["Latitude"].values) ** 2 +
        (site_data["Longitude"].values - random_sites["Longitude"].values) ** 2
    )

    # Count alignments within 1-degree threshold
    aligned_sites = np.sum(distances < 1.0)  # Adjust threshold if needed

    # Debugging: Print progress every 1000 iterations
    if i % 1000 == 0:
        print(f"🟡 Simulation {i}: {aligned_sites} alignments found")

    alignment_counts.append(aligned_sites)

# Confirm number of iterations actually stored
print(f"✅ Stored {len(alignment_counts)} alignment counts (should be 10,000)")

# Convert results to DataFrame
results_df = pd.DataFrame(alignment_counts, columns=["Number_of_Alignments"])

# Debugging: Show DataFrame preview
print("🟢 Monte Carlo results DataFrame preview:")
print(results_df.head())

# Ensure data is not empty before saving
if results_df.empty:
    print("❌ Error: DataFrame is empty, nothing to save.")
    exit()
else:
    results_df.to_csv(output_path, index=False)
    print(f"✅ Monte Carlo simulation results saved to {output_path}")

# Verify the file was created and contains data
time.sleep(2)  # Pause before checking file

if os.path.exists(output_path):
    df_check = pd.read_csv(output_path)
    if df_check.empty:
        print("❌ Error: The saved CSV file is empty!")
    else:
        print(f"✅ Saved CSV file contains {len(df_check)} records.")
else:
    print("❌ Error: CSV file was not created!")

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
print(f"✅ p-value of observed alignment: {p_value:.5f}")

print("✅ Monte Carlo simulation completed successfully.")