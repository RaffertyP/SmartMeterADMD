pacman::p_load(readr, data.table, ggplot2, lubridate, dplyr)

dPathGeneral <- "C:/Users/ParkerR/Data/"
dPathProject <- paste0(here::here(), "/data/")
pPath <- paste0(here::here(), "/plots/")

VectorColours <- read_csv(paste0(dPathGeneral, "VectorColours.csv"))

DT <- as.data.table(
  read_csv(paste0(dPathProject, "AllColdEveningsData.csv"))
)

DT$Power <- DT$kWh*2
DT$HalfHourTimeStamp <- paste0(DT$DateKey, DT$TradingPeriodNumber)

DT_attrib <- as.data.table(read_csv(
  paste0(dPathGeneral, "VectorICPAttributes.csv"),
  col_types = cols(
    ART33 = col_skip(),
    CustomerType = col_skip(),
    DGFlag = col_skip(),
    FeederCode = col_skip(),
    ICP_Property_Category = col_skip(),
    LPGFlag = col_skip(),
    MB2018 = col_skip(),
    NetworkZone = col_skip(),
    OccupierFlag = col_skip(),
    Platform = col_skip(),
    PriceGroup = col_skip(),
    RevenueGroup = col_skip(),
    kWh2019 = col_skip()
  )
 )
)

DT_attrib <- DT_attrib[ICP %in% unique(DT$ICP)]

process_and_plot <- function(DT, saveName, nIterations, maxHouseholds, Percentile){
  df_i <- data.frame(
    Iteration=numeric(),
    NHouseholds=numeric(),
    ADMD=numeric(),
    HalfHourTimestamp = as.Date(character()),
    stringsAsFactors=FALSE
  )
  df_n <- data.frame(
    Iteration=numeric(),
    NHouseholds=numeric(),
    ADMD=numeric(),
    HalfHourTimestamp = as.Date(character()),
    stringsAsFactors=FALSE
  )
  iterations <- seq(1:nIterations)
  NHouseholds <- seq(1:maxHouseholds)
  for (n in NHouseholds){
    for (i in iterations) {
      list <- sample(unique(DT$ICP), n)
      df_power_temp <- DT[ICP %in% list] %>%
        group_by(HalfHourTimeStamp) %>%
        summarise(totalPower = sum(Power, na.rm = TRUE))
      df_power_temp$ADMD <- df_power_temp$totalPower/n
      df_temp <- df_power_temp[df_power_temp$ADMD == max(df_power_temp$ADMD), 
                                  c('HalfHourTimeStamp', 'ADMD')]
      df_temp$Iteration <- i
      df_temp$NHouseholds <- n
      df_i <- rbind(df_i, df_temp)
    }
    df_n <- rbind(df_n, df_i)
  }
  
  df_unique <- unique(df_n)
  df_unique$date = as_date(substr(df_unique$HalfHourTimeStamp, 1, 8))
  df_unique$tp = substr(df_unique$HalfHourTimeStamp, 9, 10)
  
  ADMD_df <- df_unique %>%
    group_by(NHouseholds) %>%
    summarise(meanADMD = mean(ADMD), 
              minADMD = min(ADMD),
              maxADMD = max(ADMD),
              percentile95th = quantile(ADMD, probs = Percentile/100))

 # The following line is used when manually relaoding data and saving smoothed plots
 # ADMD_df <- read_csv(paste0("data/diversity_demand_", saveName, ".csv"))
  
  ADMD_df$percentile_95th_smoothed <-
    loess(percentile95th ~ NHouseholds, data = ADMD_df, span = 0.3)$fitted
  
  write_csv(ADMD_df, paste0(dPathProject, "diversity_demand_",nIterations, 
                            '_iterations_', saveName, ".csv"))
  
  p2 <- ggplot(ADMD_df) + 
    geom_line(aes(x = NHouseholds, y = percentile_95th_smoothed), 
              size = 1.5, colour = VectorColours$hex[1]) +
    theme_minimal() +
    theme(text = element_text(size = 18)) +
    scale_y_continuous(limits = c(0, max(ADMD_df$percentile_95th_smoothed)))
  p2 + labs(y='ADMD (kW)', x = 'Number of households')
  ggsave(paste0(pPath, saveName, '_', nIterations, "_iterations_", Percentile, 
                'th_percentile_smoothed.png'), 
         height = 6, width = 12)
}

start_time <- Sys.time()
# House, elec only
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 0]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_Elec",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)
end_time <- Sys.time()
end_time - start_time
# Time difference of 31.7981 mins

# House dual fuel (elec and gas) 
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 1]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_Dual",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)
# Attached Elec
ICPlist <- DT_attrib[CategoryDwelling2 == 'Attached' & GasFlag == 0]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "Attached_Elec",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# Attached Dual
ICPlist <- DT_attrib[CategoryDwelling2 == 'Attached' & GasFlag == 1]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "Attached_Dual",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# Lifestyle
ICPlist <- DT_attrib[CategoryDwelling2 == 'Lifestyle']$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "Lifestyle",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House old Elec
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 0 & kWhStartYear <= 2006]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_Old_Elec",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House 2006 to 2012 Elec
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 0 
                     & kWhStartYear %in% c(2007, 2008, 2009, 2010, 2011, 2012)]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_2006_to_2012_Elec",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House 2006 to 2012 dual
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 1 & 
                       kWhStartYear %in% c(2007, 2008, 2009, 2010, 2011, 2012)]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_2006_to_2012_Dual",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House new Elec
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 0 
                     & kWhStartYear > 2012]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_New_Elec",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House new dual
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 1 & 
                       kWhStartYear > 2012]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_New_Dual",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House old Dual
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & GasFlag == 1 & kWhStartYear <= 2006]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_Old_Dual",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House small floor area
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & ICP_Property_Floor_Area < 100]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_Small",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House medium floor area
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' &
                       ICP_Property_Floor_Area > 100 & ICP_Property_Floor_Area < 200]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_Medium",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)

# House large floor area
ICPlist <- DT_attrib[CategoryDwelling2 == 'House' & ICP_Property_Floor_Area > 200]$ICP
DT_tmp <- DT[ICP %in% ICPlist]
process_and_plot(
  DT_tmp,
  saveName = "House_Large",
  nIterations = 20,
  maxHouseholds = 200,
  Percentile = 95
)
