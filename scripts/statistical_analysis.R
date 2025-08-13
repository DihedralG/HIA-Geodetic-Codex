import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# Define paths
repo_root = os.getcwd()
data_dir = os.path.join(repo_root, "HIA-Geodetic-Codex/data")

# Load the Monte Carlo results dataset
input_csv_path = os.path.join(data_dir, "mc_simulation_results.csv")

if not os.path.exists(input_csv_path):
    print(f"❌ Error: Monte Carlo results file not found at {input_csv_path}")
    exit()

df = pd.read_csv(input_csv_path)

# Check if the dataset contains valid data
if df.empty:
    print("❌ Error: The dataset is empty. No statistical analysis can be performed.")
    exit()

# Basic descriptive statistics
summary_stats = df.describe()

# Compute additional statistics
median_alignments = np.median(df["Number_of_Alignments"])
mode_alignments = stats.mode(df["Number_of_Alignments"])[0][0]
variance = np.var(df["Number_of_Alignments"])
skewness = stats.skew(df["Number_of_Alignments"])
kurtosis = stats.kurtosis(df["Number_of_Alignments"])

# Combine results into a DataFrame
extended_stats = pd.DataFrame({
    "Statistic": ["Mean", "Median", "Mode", "Variance", "Standard Deviation", "Skewness", "Kurtosis"],
    "Value": [
        summary_stats.loc["mean", "Number_of_Alignments"],
        median_alignments,
        mode_alignments,
        variance,
        summary_stats.loc["std", "Number_of_Alignments"],
        skewness,
        kurtosis
    ]
})

# Save statistical results to a CSV file
output_csv_path = os.path.join(data_dir, "statistical_results.csv")
extended_stats.to_csv(output_csv_path, index=False)

print(f"✅ Statistical analysis results saved to {output_csv_path}")

# Generate histogram for visualization
plt.figure(figsize=(8, 5))
plt.hist(df["Number_of_Alignments"], bins=50, color="blue", alpha=0.7, label="Monte Carlo Alignments")
plt.axvline(summary_stats.loc["mean", "Number_of_Alignments"], color="red", linestyle="dashed", label="Mean Alignment Count")
plt.xlabel("Number of Alignments")
plt.ylabel("Frequency")
plt.title("Monte Carlo Simulation: Distribution of Site Alignments")
plt.legend()
plt.grid(True)
plt.show()