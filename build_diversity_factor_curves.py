# Load packages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import numpy as np

# Read data
df = pd.read_csv('data/kW2022_WinterPeakMetered.csv')

# Remove kW2022_WinterPeakMetered values greater than 70 (3 phase 100A + 69kVA)
df = df[df['kW2022_WinterPeakMetered'] < 70]

# Group by DwellingType and calculate mean of kW2022_WinterPeakMetered
df_grouped_mean = df.groupby('DwellingType')['kW2022_WinterPeakMetered'].mean()

# Commented chunk below takes a long time to run, so I have saved the results to a csv file
##############################################################################################################
##############################################################################################################
# # For each DwellingType, and for numbers n = 1 to 100, randomly select a sample of size n 200 times
# # then sum kW2022_WinterPeakMetered for each sample, calculate the 99th percentile of the sum, and divide it by n
# df_grouped_percentile = pd.DataFrame()
# for dwelling_type in df['DwellingType'].unique():
#     print(dwelling_type)
#     df_dwelling_type = df[df['DwellingType'] == dwelling_type]
#     percentile_list = []
#     for n in range(1, 101):
#         print(f'Number of ICPs: {n}')
#         percentile_sum_list = []
#         for i in range(200):
#             df_sample = df_dwelling_type.sample(n)
#             sample_sum = df_sample['kW2022_WinterPeakMetered'].sum()
#             #print(f'sample {i}: {sample_sum}')
#             percentile_sum_list.append(sample_sum)
#         percentile_list.append(pd.Series(percentile_sum_list).quantile(0.99) / n)
#     df_grouped_percentile[dwelling_type] = percentile_list


# # Divide each column by the mean of kW2022_WinterPeakMetered for each DwellingType
# for dwelling_type in df['DwellingType'].unique():
#     df_grouped_percentile[dwelling_type] = df_grouped_percentile[dwelling_type] / df_grouped_mean[dwelling_type]

# # Create new column in df_grouped_percentile that is the mean of all DwellingTypes
# df_grouped_percentile['mean'] = df_grouped_percentile.mean(axis=1)

# # Create new column in df_grouped_percentile called 'NumberOfICPs' that is the index plus 1
# df_grouped_percentile['NumberOfICPs'] = df_grouped_percentile.index + 1

# # Set NumberOfICPs as the index
# df_grouped_percentile.set_index('NumberOfICPs', inplace=True)

# # Save df_grouped_percentile to a csv file
# df_grouped_percentile.to_csv('data/df_grouped_percentile.csv', index=True)
##############################################################################################################
##############################################################################################################

# Read df_grouped_percentile from csv file
df_grouped_percentile = pd.read_csv('data/df_grouped_percentile.csv', index_col=0)

# Extract column names for plotting
colnames = df['DwellingType'].unique().tolist()

# Create a list of colors to be used for each line plot
colors = plt.cm.tab20(np.linspace(0, 1, len(colnames)))

# Set size of plot
plt.figure(figsize=(10, 6))

# Create line plot of df_grouped_percentile for each DwellingType
for i, column in enumerate(colnames):
    #print(i, column)
    plt.plot(df_grouped_percentile[column], label=column, color=colors[i])

plt.legend()
plt.title('Diversity factor for each dwelling type 2022')
plt.grid(True)
plt.ylim(0)
# Set axis labels
plt.xlabel('Number of ICPs')
plt.ylabel('Diversity factor')
plt.savefig('plots/diversity_factor_by_dwelling_type_2022.png')
#plt.show()

plt.close()

# Set size of plot
plt.figure(figsize=(10, 6))
# Restict data to between where index is between 0 and 10 and replot
df_grouped_percentile_restricted = df_grouped_percentile.iloc[0:11, :]
for i, column in enumerate(colnames):
    plt.plot(df_grouped_percentile_restricted[column], label=column, color=colors[i])

plt.legend()
plt.title('Diversity factor for each dwelling type 2022')
plt.grid(True)
# Set axis labels
plt.xlabel('Number of ICPs')
plt.ylabel('Diversity factor')
plt.ylim(0)
plt.xlim(0)
plt.yticks(range(0, 7))
plt.savefig('plots/diversity_factor_by_dwelling_type_2022_0_to_10.png')
plt.show()
