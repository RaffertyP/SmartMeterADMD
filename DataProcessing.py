# Pull from database
import pyodbc
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
#from plotnine import ggplot as gg
VectorColours = pd.read_csv('C:/Users/ParkerR/Data/VectorColours.csv')

cnxn = pyodbc.connect('Trusted_connection=yes', driver='ODBC Driver 17 for SQL Server', server="AKLSABI01", database="Customer")

# query = "SELECT * \
# FROM dbo.ICPkW2015_WinterPeakHHDB"

#df_original = pd.read_sql(query, cnxn)
hhr_df = pd.read_csv("C:/Users/ParkerR/SmartEVChargingPh2/Data/DataGenerators/Source/2015_Trialists_Consumption_INC_WAIHEKE.csv")
EV_ICP_list = hhr_df['ICP'].unique()

# df = df_original[df_original['ICP'].isin(EV_ICP_list)]

query = "SELECT DISTINCT ICP, Retailer, Region, CustomerType, kW2015_WinterPeakMetered, ICP_Property_Category, GasFlag \
FROM Customer.dbo.ICPdataElec20 \
WHERE kW2015_WinterPeakMetered IS NOT NULL"
df_original = pd.read_sql(query, cnxn)

#diversity = diversity_list[0]
# Now we may filter (only residential, etc)
# Where customer = residential, gas flag = 0/1
# council property type = apartment

def model_and_plot(df, savename, demand_colname, n_iterations, max_diversity):
    admd_instance = np.zeros([n_iterations, 2])
    admd_99th_pc = np.zeros([max_diversity, 1])
    iterations = range(1, n_iterations + 1)
    diversity_list = range(1, max_diversity + 1)
    for diversity in diversity_list:
        for iteration in iterations:
            df_subset = df.sample(n=diversity)
            admd_instance[(iteration - 1)] = (diversity, sum(df_subset[demand_colname]) / diversity)
        admd_99th_pc[diversity - 1, :] = [np.percentile(admd_instance[:, 1], 99)]

    admd_df = pd.DataFrame(admd_99th_pc, columns=['99th_percentile'])
    admd_df['diversity'] = range(1, max_diversity+1)
    admd_df.to_csv('data/' + savename + '.csv', index= False)
    # plot
    plt.plot(admd_df['diversity'], admd_df['99th_percentile'], color=VectorColours['hex'][0])
    plt.title('Demand over cold winter evenings')
    plt.xlabel('Diversity')
    plt.ylabel('Demand (kW)')
    plt.ylim(ymin=0)
    plt.grid(color='grey', linestyle='-', linewidth=1, alpha = 0.5)
    plt.show()
    plt.savefig('plots/ColdEveningAverages/' + savename + '.png')

df_gas = df_original[df_original['GasFlag'] == 1]
df_gas_residential = df_original[(df_original['CustomerType'] == 'Residential') & (df_original['GasFlag'] == 1)]
df_no_gas_residential_dwelling = df_original[(df_original['GasFlag'] == 0) & (df_original['CustomerType'] == 'Residential')]
df_no_gas_apartments = df_original[(df_original['GasFlag'] == 0) & (df_original['CustomerType'] == 'Residential')]

df_no_gas_residential_dwelling_large_values = df_no_gas_residential_dwelling[df_no_gas_residential_dwelling['kW2015_WinterPeakMetered'] > 14]
df_no_gas_residential_dwelling_large_values_removed = df_no_gas_residential_dwelling[df_no_gas_residential_dwelling['kW2015_WinterPeakMetered'] < 14]

model_and_plot(df_no_gas_apartments, "99th_pc_admd_no_gas_residential_apartments", 'kW2015_WinterPeakMetered', n_iterations=1000, max_diversity=100)
model_and_plot(df_no_gas_residential_dwelling_large_values_removed, "99th_pc_admd_no_gas_residential_apartments_large_values_removed", 'kW2015_WinterPeakMetered', n_iterations=1000, max_diversity=100)

model_and_plot(df_gas, "99th_pc_admd_gas_customers", 'kW2015_WinterPeakMetered', n_iterations=1000, max_diversity=100)
model_and_plot(df_gas_residential, "99th_pc_admd_gas_residential_rental_flats_customers", 'kW2015_WinterPeakMetered', n_iterations=1000, max_diversity=100)
model_and_plot(df_no_gas_residential_dwelling, "99th_pc_admd_no_gas_residential_dwelling_customers", 'kW2015_WinterPeakMetered', n_iterations=1000, max_diversity=100)
model_and_plot(df_original, "99th_pc_admd_all", 'kW2015_WinterPeakMetered', n_iterations=1000, max_diversity=100)

df_20150624_tp_38 = pd.read_csv("C:/Users/ParkerR/SmartMeterADMD/data/All_ICPs_20150624_tp38.csv")
df_20150624_tp_38 = df_20150624_tp_38[df_20150624_tp_38['kW'] > 0.001]
df = df_20150624_tp_38[df_20150624_tp_38['ICP'].isin(EV_ICP_list)]

model_and_plot(df, "99th_pc_EV_trialists_20150624_tp38", 'kW', n_iterations=100, max_diversity=100)

df_residential_no_gas = df_20150624_tp_38[(df_20150624_tp_38['CustomerType'] == 'Residential') & (df_20150624_tp_38['GasFlag'] == 0)]
model_and_plot(df_residential_no_gas, "99th_pc_admd_no_gas_residential_20150624_tp_38", 'kW', n_iterations=100, max_diversity=100)

df_residential_with_gas = df_20150624_tp_38[(df_20150624_tp_38['CustomerType'] == 'Residential') & (df_20150624_tp_38['GasFlag'] == 1)]
model_and_plot(df_residential_with_gas, "99th_pc_admd_with_gas_residential_20150624_tp_38", 'kW', n_iterations=100, max_diversity=100)





#############################################################
# n_iterations = 1000
max_diversity = 100

admd_instance = np.zeros([n_iterations, 2])
admd_min_max_mean = np.zeros([max_diversity, 3])

iterations = range(1,n_iterations+1)
diversity_list = range(1,max_diversity+1)

# diversity = 1

for diversity in diversity_list:
    for iteration in iterations:
        df_subset = df.sample(n=diversity)
        admd_instance[(iteration-1)] = (diversity, sum(df_subset['kW2015_WinterPeakMetered']) / diversity)
    admd_min_max_mean[diversity-1,:] = [admd_instance[:,1].min(), admd_instance[:,1].max(), admd_instance[:,1].mean()]

admd_df = pd.DataFrame(admd_min_max_mean, columns = ['min', 'max', 'mean'])
admd_df['diversity'] = range(1, max_diversity+1)

# Now save
admd_df.to_csv('data/EVTrialistsOnly_WinterPeakHHDB_mean_min_max.csv', index=False)

# read data
# admd_df = pd.read_csv('data/allICPkW2015_WinterPeakHHDB_mean_min_max.csv')


plt.fill_between(admd_df['diversity'], admd_df['min'], admd_df['max'], color=VectorColours['hex'][1])
plt.plot(admd_df['diversity'], admd_df['mean'], color=VectorColours['hex'][0])
plt.title('Average demand over cold winter evenings')
plt.xlabel('Diversity')
plt.ylabel('Demand (kW)')
#plt.show()
plt.savefig('plots/EV_trial_participants_admd_with_ribbon_cold_winter_averages.png')


plt.plot(admd_df['diversity'], admd_df['mean'], color=VectorColours['hex'][0])
plt.title('Average demand over cold winter evenings')
plt.xlabel('Diversity')
plt.ylabel('Demand (kW)')
plt.show()
plt.savefig('plots/EV_trial_participants_admd_cold_winter_averages.png')

