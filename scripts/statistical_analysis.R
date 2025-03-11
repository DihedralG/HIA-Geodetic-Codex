import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats import weightstats as stests
import matplotlib.pyplot as plt

# Load your dataset
# Ensure your dataset is loaded correctly; replace 'your_dataset.csv' with your actual file
# df = pd.read_csv('your_dataset.csv')

# For demonstration purposes, let's create a sample dataset
np.random.seed(0)
data_group1 = np.random.normal(loc=50, scale=5, size=100)
data_group2 = np.random.normal(loc=52, scale=5, size=100)
data_paired1 = np.random.normal(loc=50, scale=5, size=100)
data_paired2 = data_paired1 + np.random.normal(loc=0, scale=2, size=100)

# 1. Shapiro-Wilk Test for Normality
def shapiro_wilk_test(data):
    stat, p_value = stats.shapiro(data)
    return stat, p_value

# 2. Levene Test for Equal Variance
def levene_test(data1, data2):
    stat, p_value = stats.levene(data1, data2)
    return stat, p_value

# 3. Independent T-Test (Student's T-Test)
def independent_t_test(data1, data2, equal_var=True):
    stat, p_value = stats.ttest_ind(data1, data2, equal_var=equal_var)
    return stat, p_value

# 4. Paired T-Test
def paired_t_test(data1, data2):
    stat, p_value = stats.ttest_rel(data1, data2)
    return stat, p_value

# 5. Mann-Whitney U Test (Non-Parametric)
def mann_whitney_u_test(data1, data2):
    stat, p_value = stats.mannwhitneyu(data1, data2)
    return stat, p_value

# 6. Wilcoxon Signed-Rank Test (Non-Parametric, Paired)
def wilcoxon_signed_rank_test(data1, data2):
    stat, p_value = stats.wilcoxon(data1, data2)
    return stat, p_value

# 7. One-Way ANOVA
def one_way_anova(*groups):
    stat, p_value = stats.f_oneway(*groups)
    return stat, p_value

# 8. Kruskal-Wallis H Test (Non-Parametric ANOVA)
def kruskal_wallis_test(*groups):
    stat, p_value = stats.kruskal(*groups)
    return stat, p_value

# 9. Chi-Squared Test
def chi_squared_test(observed, expected):
    stat, p_value = stats.chisquare(f_obs=observed, f_exp=expected)
    return stat, p_value

# 10. Pearson Correlation Coefficient
def pearson_correlation(x, y):
    corr_coef, p_value = stats.pearsonr(x, y)
    return corr_coef, p_value

# 11. Spearman Rank Correlation
def spearman_rank_correlation(x, y):
    corr_coef, p_value = stats.spearmanr(x, y)
    return corr_coef, p_value

# Example usage
if __name__ == "__main__":
    # Shapiro-Wilk Test
    stat, p = shapiro_wilk_test(data_group1)
    print(f'Shapiro-Wilk Test: Statistics={stat}, p={p}')

    # Levene Test
    stat, p = levene_test(data_group1, data_group2)
    print(f'Levene Test: Statistics={stat}, p={p}')

    # Independent T-Test
    stat, p = independent_t_test(data_group1, data_group2)
    print(f'Independent T-Test: Statistics={stat}, p={p}')

    # Paired T-Test
    stat, p = paired_t_test(data_paired1, data_paired2)
    print(f'Paired T-Test: Statistics={stat}, p={p}')

    # Mann-Whitney U Test
    stat, p = mann_whitney_u_test(data_group1, data_group2)
    print(f'Mann-Whitney U Test: Statistics={stat}, p={p}')

    # Wilcoxon Signed-Rank Test
    stat, p = wilcoxon_signed_rank_test(data_paired1, data_paired2)
    print(f'Wilcoxon Signed-Rank Test: Statistics={stat}, p={p}')

    # One-Way ANOVA
    stat, p = one_way_anova(data_group1, data_group2)
    print(f'One-Way ANOVA: Statistics={stat}, p={p}')

    # Kruskal-Wallis Test
    stat, p = kruskal_wallis_test(data_group1, data_group2)
    print(f'Kruskal-Wallis Test: Statistics={stat}, p={p}')

    # Chi-Squared Test
    observed = [10, 20, 30]
    expected = [15, 15, 30]
    stat, p = chi_squared_test(observed, expected)
    print(f'Chi-Squared Test: Statistics={stat}, p={p}')

    # Pearson Correlation
    corr_coef, p = pearson_correlation(data_group1, data_group2)
    print(f'Pearson Correlation: Coefficient={corr_coef}, p={p}')

    # Spearman Rank Correlation
    corr_coef, p = spearman_rank_correlation(data_group1, data_group2)
    print(f'Spearman Rank Correlation: Coefficient={corr_coef}, p={p}')