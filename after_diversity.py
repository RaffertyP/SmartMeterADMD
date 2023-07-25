# import subprocess
# subprocess.call(["pip", "-q", "install", "pandas==1.2.3"])
# subprocess.call(["pip", "-q", "install", "pyathena==1.11.2"])

import io
import numpy as np
import pandas as pd
import random

import matplotlib.pyplot as plt

import seaborn as sns
sns.set_style("whitegrid")

import boto3
s3 = boto3.resource('s3')

import pyodbc

def import_data(sql_query, driver, server, db):
    """
    Uses the pyodbc connection to extract data from SABI in the data warehouse
    """
    
    # Establishing a connection
    cnxn = pyodbc.connect(f"Driver={driver};"
                          f"Server={server};"
                          f"Database={db};"
                          "Trusted_Connection=yes;")
    
    # load the data
    df = pd.read_sql(sql_query, cnxn)
                       
    return df


# 75th Percentile
def q75(x):
    return x.quantile(0.75)

# 90th Percentile
def q90(x):
    return x.quantile(0.9)

# 95th Percentile
def q95(x):
    return x.quantile(0.95)

########################### Replace this section with the correct random sample data import ####################################
# icps_query = """
#     SELECT
#          ide.ICP
#         ,ide.[ART33]
#         ,ide.[Platform]
#         ,ide.[FeederCode]
#         ,ide.[NetworkZone]
#         ,ide.[CustomerType]
#         ,ide.[RevenueGroup]
#         ,pp.PriceGroup
#         ,ide.[kWhStartYear]
#         ,ide.[kWh2019]
#         ,ide.[ICP_Property_Category]
#         ,ide.[ICP_Property_Floor_Area]
#         ,ide.[GasFlag]
#         ,ide.[LPGFlag]
#         ,ide.[DGFlag]
#         ,ide.[DeprivationDecile]
#         ,ide.[MB2018]
#         ,ide.[OccupierFlag]
#     FROM [ICPdataElec20] ide
#     JOIN dbo.PricePlan pp ON pp.PricePlan = ide.PricePlan
#     WHERE ide.CustomerType = 'Residential'
# """
#
# icps = import_data(icps_query, "ODBC Driver 17 for SQL Server", "aklsabi01", "Customer")
#
# icps = pd.read_csv("data/All_ICPs_20150624_tp38.csv")
#
# sample_icps = icps.sample(1000, random_state=42).ICP
# t = tuple(sample_icps)
#
# meter_query = """
#     SELECT
#         i.ICP as icp
#         ,dd.DateKey as reading_date
#         ,f.TradingPeriodNumber as trading_period
#         ,f.KilowattHours AS kWh
#     FROM    NDS.MeterData.vfactMeterPollData f
#             JOIN NDS.MeterData.vdimEnergyFlowDirection e ON e.EnergyFlowDirectionKey = f.EnergyFlowDirectionKey
#             JOIN NDS.VectorEM.dimDate dd ON dd.DateKey = f.MeterPollDateKey
#             JOIN NDS.VectorEM.dimICP i ON i.ICPKey = f.ICPKey
#     WHERE    f.UseForReportingFlag = 1 -- This filters out duplicates which may or may not be valid
#             AND e.EnergyFlowDirectionCode = 'X' --X is consumption and I is distributed generation injection
#             AND f.TradingPeriodNumber NOT IN (49, 50)
#             AND i.icp in {}
# """.format(t)
#
# meter_df = import_data(meter_query, "ODBC Driver 17 for SQL Server", "aklbi03pi", "NDS")
#
# meter_df.to_csv("1000_sample.csv", index=False)

###############################################################################################################################

meter_df = pd.read_csv(r'C:\Users\ParkerR\SmartMeterADMD\1000_sample.csv')

from time import process_time

t1_start = process_time()

random_icp_df = meter_df
# Creating hour of year column. Takes ~ 15sec
random_icp_df["hour"] = (random_icp_df.trading_period/2 + 1/2).astype("int").astype("str")

random_icp_df = random_icp_df.sort_values(['icp', 'reading_date', 'trading_period'], ignore_index=True)

# icp_summary = random_icp_df['icp'].sum()

random_icp_df['date_tp'] = random_icp_df.reading_date.astype("str") + random_icp_df.trading_period.astype("str").str.zfill(2)

#random_icp_df["hour_of_year"] = random_icp_df.reading_date.astype("str") + random_icp_df.hour.str.zfill(2)

# Dropping unused columns
random_icp_df = random_icp_df.drop(columns=["trading_period", "reading_date", "hour"])
# Grouping to hourly level
#random_icp_df = random_icp_df.groupby(["icp" ,"date_tp"]).sum().reset_index()

# Selecting 1 year of data
random_icp_df = random_icp_df.loc[(random_icp_df.date_tp >= '2015070101') & (random_icp_df.date_tp < '2016070102')]

#tst_df =  random_icp_df.loc[random_icp_df["count"] > 1.65e+04]

# Removing icps that don't have a full year of data
random_icp_df['count'] = random_icp_df.groupby(['icp'])['icp'].transform('count')
random_icp_df = random_icp_df.loc[random_icp_df["count"] == 1.756700e+04]

random_icp_df['kW'] = random_icp_df["kWh"]*2
# Creating a column of zeros to use as a join key
random_icp_df["join_key"] = 0

random_icp_df = random_icp_df.drop(columns=["kWh", "count"])

# Creating a zeros df to use as a join key
sample_df = pd.DataFrame(np.zeros(shape=(20, 1)))
# Resetting the index to use as a sample number
sample_df = sample_df.reset_index()
sample_df.columns = ["S", "join_key"]

# Using the join key for a full outer join with the sample (duplicating the data 20 times). Takes ~ 15sec
full_df = sample_df.merge(random_icp_df).drop(columns="join_key")

# Shuffling the data. Takes ~ (40 sec)
shuffle_df = full_df.drop_duplicates(subset=["S", "icp"])
shuffle_df = shuffle_df.sample(frac=1,  random_state=42).sort_values(by=["S"])
full_df = shuffle_df.drop(columns=["kW", "date_tp"]).merge(full_df, how="left", on=["S", "icp"])

# Calculating the cumulative mean. Takes ~ (1 min)
full_df["AD"] = (full_df.groupby(['date_tp', 'S'])["kW"].cumsum() / 
                 (full_df.groupby(['date_tp', 'S'])["kW"].cumcount()+1))

full_df["order"] = full_df.groupby(['date_tp', 'S']).cumcount()

full_df = full_df.drop(columns=["icp", "date_tp", "kW"])

after_diversity_df = (full_df.groupby(['S','order'])
                             .agg({"AD": ["count", "max", "min", "mean", "median", q75, q90, q95]})
                             .reset_index(drop=False))

after_diversity_df.columns = ["".join(x) for x in after_diversity_df.columns.ravel()]

# Plotting the figures. Takes about 2 min
fig, ax = plt.subplots(8, 1, figsize=(25, 50))

sns.lineplot('order', 'ADmax', data=after_diversity_df, ax=ax[0])

sns.lineplot('order', 'ADq95', data=after_diversity_df, ax=ax[1])

sns.lineplot('order', 'ADq90', data=after_diversity_df, ax=ax[2])

sns.lineplot('order', 'ADq75', data=after_diversity_df, ax=ax[3])

sns.lineplot('order', 'ADmean', data=after_diversity_df, ax=ax[4])

sns.lineplot('order', 'ADmedian', data=after_diversity_df, ax=ax[5])

sns.lineplot('order', 'ADmin', data=after_diversity_df, ax=ax[6])

sns.lineplot('order', 'ADcount', data=after_diversity_df, ax=ax[7])

plt.show()

t1_stop = process_time()
print("Elapsed time in seconds:", t1_stop-t1_start)

# Elapsed time in seconds: 462.609375