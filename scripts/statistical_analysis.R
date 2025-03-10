# R script for statistical testing
# Statistical Analysis of Site Alignments

# Load necessary libraries
library(ggplot2)
library(dplyr)
library(sp)
library(sf)

# Load site coordinates
site_data <- read.csv("data/site_coordinates.csv")

# Monte Carlo results
mc_results <- read.csv("data/mc_simulation_results.csv")

# Compute basic statistics
summary_stats <- site_data %>%
  summarise(
    mean_lat = mean(Latitude),
    mean_lon = mean(Longitude),
    sd_lat = sd(Latitude),
    sd_lon = sd(Longitude)
  )

print("Summary Statistics for Site Data:")
print(summary_stats)

# Perform spatial autocorrelation test (Moran's I)
coordinates(site_data) <- ~Longitude + Latitude
moran_test <- spdep::moran.test(site_data$Latitude, listw = spdep::nb2listw(spdep::knn2nb(spdep::knearneigh(coordinates(site_data), k=4))))

print("Moran's I Test for Spatial Autocorrelation:")
print(moran_test)

# Visualize results
ggplot(mc_results, aes(x = Number_of_Alignments)) +
  geom_histogram(fill = "blue", alpha = 0.6, bins = 50) +
  geom_vline(aes(xintercept = length(site_data$Latitude)), color = "red", linetype = "dashed") +
  labs(title = "Monte Carlo Simulation of Site Alignments", x = "Number of Alignments", y = "Frequency") +
  theme_minimal()
