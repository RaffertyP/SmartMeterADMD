# This script fits a curve to the precalculated divergence data 
# in order to determine an equation for the diversity factor as a function of the number of ICPs.

# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load data
df = pd.read_csv('data/df_grouped_percentile.csv')

# Set column 'NumberOfICPs' as the index
df.set_index('NumberOfICPs', inplace=True)

# Take mean of all DwellingTypes
df['mean'] = df.mean(axis=1)

# # Restrict data to NumberOfICPs between 1 and 30
# df = df[(df.index >= 1) & (df.index <= 30)]

# Define the function to fit the data to
def curve_func(x, A, B):
    return (A + B * x) / (1 + B * x)

# Extract x values from the DataFrame index and y values from the 'mean' column
x_data = df.index.values
y_data = df['mean'].values

# Perform the curve fitting
params, cov = curve_fit(curve_func, x_data, y_data, p0=[10, 10])  # Provide an initial guess for parameters A and B

# Extract the parameters
#A_fit, B_fit = params
# Parameters specified befow obtained by restricting the data to less than 30 ICPs
# These fit the low-numbers data better, and drop to 1 faster which is more realistic
A_fit = 4.75
B_fit = 0.49

#DF = (4.75 + 0.49 N) / (1 + 0.49 * N)
# (A + B * x) / (1 + B * x)

# Create a new DataFrame with the fitted values
x_fit = np.linspace(x_data.min(), x_data.max(), 100)  # Generate x values for the fitted curve
y_fit = curve_func(x_fit, A_fit, B_fit)
#y_fit = curve_func(x_fit, B_fit)

# Build the fitted curve for n = 1 to 300 as per Kelvin's request
x_fit_300 = np.linspace(1, 300, 300)  # Generate x values for the fitted curve
y_fit_300 = curve_func(x_fit_300, A_fit, B_fit)

# Set size of plot
plt.figure(figsize=(10, 6))

# Plot the fitted curve for n = 1 to 300 with thick line
plt.plot(x_fit_300, y_fit_300, label='Fitted curve', color='#000840', linewidth=3)
plt.xlabel('Number of ICPs')
plt.ylabel('Diversity factor')

# Set x tick marks to be every 20
plt.xticks(np.arange(0, 301, 20))

# Set y tick marks to be every 0.2
plt.yticks(np.arange(1, 3.8, 0.2))

# Add gridlines
plt.grid(True)

# Save the plot
plt.savefig('plots/diversity_factor_fitted_curve.png', dpi=300)

# # Plot the original data and the fitted curve
# plt.scatter(x_data, y_data, label='Data')
# plt.plot(x_fit, y_fit, label='Fitted curve', color='red')
# plt.xlabel('Number of ICPs')
# plt.ylabel('Diversity factor')
# plt.grid(True)
# plt.ylim(0)
# plt.legend()
# plt.show()

# Now plot all the DwellingTypes on the same plot along with the fitted curve

# Create a list of colors to be used for each line plot
colors = plt.cm.tab20(np.linspace(0, 1, len(df.columns) - 1))

# Create a larger figure
plt.figure(figsize=(10, 6))

# Create line plot of df_grouped_percentile for each DwellingType
for i, column in enumerate(df.columns[:-1]):
    #print(i, column)
    plt.plot(df[column], label=column, color=colors[i])

plt.plot(x_fit, y_fit, label='Fitted curve', color='red')
plt.legend()
plt.title('Diversity factor for each dwelling type 2022')
plt.grid(True)
plt.ylim(0)
# Add labels to the x and y axes
plt.xlabel('Number of ICPs')
plt.ylabel('Diversity factor')
plt.xlim(0)
plt.yticks(range(0, 5))
#plt.show()

# Adjust the resolution (DPI) to make the plot higher resolution
plt.savefig('plots/diversity_factor_by_dwelling_type_2022_with_fitted_curve.png', dpi=300)
