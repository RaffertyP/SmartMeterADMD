# Load packages
import pandas as pd
import matplotlib as plt
import seaborn as sns
import statsmodels.api as sm
from functions import build_linear_models

# Read data
df = pd.read_csv('data/kW2022_WinterPeakMetered.csv')

df.describe()

df = df[df['ICP_Property_Floor_Area'] < 1000]
df = df[df['ICP_Property_Floor_Area'] > 59]
# Remove instances where Category is Lifestyle and ICP_Property_Floor_Area > 800
df = df[~((df['DwellingType'] == 'Lifestyle') & (df['ICP_Property_Floor_Area'] > 800))]
# Remove instances where Category is Apartments and ICP_Property_Floor_Area > 300
df = df[~((df['DwellingType'] == 'Apartments') & (df['ICP_Property_Floor_Area'] > 300))]
# Remove instances where Category is Terraced and ICP_Property_Floor_Area > 400
df = df[~((df['DwellingType'] == 'Terraced') & (df['ICP_Property_Floor_Area'] > 400))]
# Remove instances where Category is Flats and ICP_Property_Floor_Area > 400
df = df[~((df['DwellingType'] == 'Flats') & (df['ICP_Property_Floor_Area'] > 400))]
# Remove instances where Category is House with Gas and ICP_Property_Floor_Area > 600
df = df[~((df['DwellingType'] == 'House with Gas') & (df['ICP_Property_Floor_Area'] > 600))]
# Remove instances where Category is House without Gas and ICP_Property_Floor_Area > 350
df = df[~((df['DwellingType'] == 'House without Gas') & (df['ICP_Property_Floor_Area'] > 350))]


# Plot histogram of ICP_Property_Floor_Area for each category
for category in df['DwellingType'].unique():
    df_category = df[df['DwellingType'] == category]
    sns.histplot(data=df_category, x='ICP_Property_Floor_Area')
    plt.title(category)
    plt.savefig('plots/FloorAreaHist/ICP_Property_Floor_Area_histogram_' + category + '.png')
    plt.close()


# Descriptive statistics
print(df.describe())

# Histogram of kW2022_WinterPeakMetered
plt.hist(df['kW2022_WinterPeakMetered'], bins=20)
plt.xlabel('kW2022_WinterPeakMetered')
plt.ylabel('Frequency')
plt.show()

# Scatter plot of floor area vs. peak electricity consumption
plt.scatter(df['ICP_Property_Floor_Area'], df['kW2022_WinterPeakMetered'])
plt.xlabel('ICP_Property_Floor_Area')
plt.ylabel('kW2022_WinterPeakMetered')
plt.show()

# Filtering
high_consumption_df = df[df['kW2022_WinterPeakMetered'] > 100]  # Example threshold value of 100 kW
print(high_consumption_df)

# Remove kW2022_WinterPeakMetered values greater than 70 (3 phase 100A + 69kVA)
df = df[df['kW2022_WinterPeakMetered'] < 70]

# Grouping and aggregation
grouped_df = df.groupby('DwellingType').agg({
    'kW2022_WinterPeakMetered': 'mean',
    'ICP_Property_Floor_Area': 'mean'
})
print(grouped_df)

# Combine 2005 and more recent data
results_df, df_regression = build_linear_models(df)

results_df.to_csv('data/lm_all_floor_area.csv')

lm_results_2005, regression_for_plotting_2005 = build_linear_models(df[df['kWhStartYear'] == 2005])
lm_results_2008_2018, regression_for_plotting_2008_2018 = build_linear_models(df[(df["kWhStartYear"] >= 2008) & (df["kWhStartYear"] <= 2018)])

regression_for_plotting_2005['YearsIncluded'] = '2005 and earlier'
lm_results_2005['YearsIncluded'] = '2005 and earlier'
regression_for_plotting_2008_2018['YearsIncluded'] = '2008 to 2018'
lm_results_2008_2018['YearsIncluded'] = '2008 to 2018'

regression_for_plotting_by_kWhStatYear = pd.concat([regression_for_plotting_2005, regression_for_plotting_2008_2018], axis=0)
lm_results_by_kWh_start_year =pd.concat([lm_results_2005, lm_results_2008_2018], axis=0)

lm_results_by_kWh_start_year.to_csv('data/lm_results_by_kWhStartYear.csv')


# Save to csv
regression_for_plotting_by_kWhStatYear.to_csv('data/regression_of_kW_peak_by_m2_sep_by_kWh_start_year.csv')

# Plot data for each DwellingType
for category_value in df_regression['DwellingType'].unique():
    df_subset = df_regression[df_regression['DwellingType'] == category_value]
    plt.plot(df_subset['ICP_Property_Floor_Area'], df_subset['kW2022_WinterPeakMetered'], label=category_value)

plt.xlabel('Dwelling floor area (m2)')
plt.ylabel('kW')
plt.title('Residential ADMD Cold Winters Day 18:00 to 19:30')
plt.legend()

# Add gridlines
plt.grid(True)

# Set the y-axis to start from 0
plt.ylim(0)

plt.savefig('plots/dwelling_type_comparison/kW2022_WinterPeakMetered_floor_area_regression.png')
plt.show()

import pandas as pd
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Assuming you already have 'regression_for_plotting_by_kWhStatYear' DataFrame from previous code

# Set size of plot
plt.figure(figsize=(10, 6))

# Create a mapping of YearsIncluded to line styles
line_styles = {
    '2005 and earlier': '--',  # Dashed line
    '2008 to 2018': '-'     # Solid line
}

# Get unique DwellingType values to assign consistent colors
dwelling_types = regression_for_plotting_by_kWhStatYear['DwellingType'].unique()
color_map = plt.cm.get_cmap('tab10', len(dwelling_types))

# Plot data for each DwellingType and YearsIncluded combination
for dwelling_type, df_dwelling_type in regression_for_plotting_by_kWhStatYear.groupby('DwellingType'):
    color = color_map(dwelling_types.tolist().index(dwelling_type))  # Get consistent color for the same DwellingType
    
    for years_included, df_subset in df_dwelling_type.groupby('YearsIncluded'):
        linestyle = line_styles[years_included]  # Set line style based on YearsIncluded
        
        plt.plot(df_subset['ICP_Property_Floor_Area'], df_subset['kW2022_WinterPeakMetered'],
                 label=f"{dwelling_type}, Years: {years_included}", linestyle=linestyle, color=color)

plt.xlabel('Floor Area (m2)')
plt.ylabel('Winter peak kW 2022')
plt.legend()

# Add gridlines
plt.grid(True)

plt.savefig('plots/WinterPeakkW2022_regression.png')
plt.show()