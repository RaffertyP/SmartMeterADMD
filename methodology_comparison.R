# this adds the ADMD equation from Sun, Konstantelos, Strbc (2016)
# to previously calculated ADMD values

pacman::p_load(readr, data.table, ggplot2, lubridate, dplyr)

dPathGeneral <- "C:/Users/ParkerR/Data/"
dPathProject <- paste0(here::here(), "/data/")
pPath <- paste0(here::here(), "/plots/")

VectorColours <- read_csv(paste0(dPathGeneral, "VectorColours.csv"))


all_dwelling_types <- c(
  "House_Elec",
  "House_Dual",
  "Attached_Elec",
  "Attached_Dual",
  "Lifestyle",
  "House_Old_Elec",
  "House_New_Elec",
  "House_2006_to_2012_Elec",
  "House_2006_to_2012_Dual",
  "House_Old_Dual",
  "House_New_Dual",
  "House_Small",
  "House_Medium",
  "House_Large"
)

##############################################
########## Equation from Sun et. al. #########
##############################################

#dwelling_types <- c("House_Small", "House_Medium", "House_Large")
#dwelling_type <- "House_Elec"

DT <- {}

for (dwelling_type in all_dwelling_types){
  
  df <- read_csv(paste0(dPathProject, 'diversity_demand_20_iterations_', 
                        dwelling_type, '.csv'))
  
  dt <- as.data.table(df)
  
  gamma <- dt$NHouseholds * min(dt$percentile_95th_smoothed)
  #gamma <- dt$NHouseholds*2
  
  alpha <- 1
  beta <- 15
  
  dt$coincident_peak_demand <-
    alpha * gamma * (1 + beta /gamma)
  
  dt$cpd_divided_by_N <- dt$coincident_peak_demand / dt$NHouseholds
  
  dt$ADMD_old_equation <- min(dt$percentile95th)*(1+3.02/dt$NHouseholds)
  
  #Create large DT of all values
 # dt$minValue <- min(dt$percentile95th)
  dt$diversity_factor <- dt$percentile_95th/min(dt$percentile95th)
  dt$dwelling_type <- dwelling_type
  DT <- rbind(DT, dt[,.(NHouseholds, percentile_95th_smoothed,cpd_divided_by_N, 
                        diversity_factor, dwelling_type)])
  
  # Prepare to plot
  dt_melted <-
    melt(dt[, .(NHouseholds, percentile95th, cpd_divided_by_N, ADMD_old_equation)], 
         id = 'NHouseholds')

  dt_melted[variable == 'cpd_divided_by_N']$variable <- "Calculated (new equation)"
  dt_melted[variable == 'ADMD_old_equation']$variable <- "Calculated (old equation)"
  dt_melted[variable == 'percentile95th']$variable <- "Computed from data"

  # Plot
  p1 <- ggplot(dt_melted, aes(x = NHouseholds, y = value, colour = variable)) +
    geom_line(size = 1.2) +
    theme_minimal() +
    scale_y_continuous(limits = c(0, max(dt_melted$value))) +
    scale_x_continuous(breaks = seq(0,200,20)) +
    scale_colour_manual(values = c(VectorColours$hex[1], 
                                   VectorColours$hex[4],
                                   VectorColours$hex[2])) +
    theme(text = element_text(size = 12))
  p1 + labs(y = 'Max demand (kW)', colour = "", x = "Number of households",
            title = paste0(dwelling_type, " ADMD comparison (computed method vs calculated methods)"))

  ggsave(paste0(pPath, "methodology_comparison/", dwelling_type, 
                "_ADMD_curve_methodology_comparison_alpha_1.png"))

}

check_DT_n200 <- DT[NHouseholds == 200]
check_DT_min <- DT %>%
  group_by(dwelling_type) %>%
  filter(percentile_95th_smoothed == min(percentile_95th_smoothed))

p2 <- ggplot(DT, aes(x = NHouseholds, y = diversity_factor, colour = dwelling_type)) +
  geom_line(size = 0.8) +
  theme_minimal() +
  scale_y_continuous(limits = c(0, max(DT$diversity_factor))) 
  scale_x_continuous(breaks = seq(0,200,20))
p2 + labs(y = "Diversity factor", x = "Number of households", colour = "Dwelling type")
ggsave(paste0(pPath, "diversity_factor_by_dwelling_type.png"))

# Make facet_grid plots comparing:
# differences between elec and dual
# differencs between for old and new

DT_50 <- DT[NHouseholds < 51]

process_dwelling_type_labels <- function(input_dt){
  input_dt[dwelling_type == "House_Elec"]$dwelling_type <- "House (electricity only)"
  input_dt[dwelling_type == "House_Dual"]$dwelling_type <- "House (dual fuel)"
  input_dt[dwelling_type == "Attached_Elec"]$dwelling_type <- "Attached (electricity only)"
  input_dt[dwelling_type == "Attached_Dual"]$dwelling_type <- "Attached (dual fuel)"
  input_dt[dwelling_type == "House_Old_Elec"]$dwelling_type <- "House (old, electricity only)"
  input_dt[dwelling_type == "House_New_Elec"]$dwelling_type <- "House (new, electricity only)"
  input_dt[dwelling_type == "House_Old_Dual"]$dwelling_type <- "House (old, dual fuel)"
  input_dt[dwelling_type == "House_New_Dual"]$dwelling_type <- "House (new, dual fuel)"
  input_dt[dwelling_type == "House_2006_to_2012_Elec"]$dwelling_type <- "House (2006 to 2012, electricity only)"
  input_dt[dwelling_type == "House_2006_to_2012_Dual"]$dwelling_type <- "House (2006 to 2012, dual fuel)"
  input_dt[dwelling_type == "House_Small"]$dwelling_type <- "House (small)"
  input_dt[dwelling_type == "House_Large"]$dwelling_type <- "House (large)"
  input_dt[dwelling_type == "House_Medium"]$dwelling_type <- "House (medium)"
  return(input_dt)
}


DT_50_labelled <- process_dwelling_type_labels(DT_50)

compare_household_types <- function(DT, dwelling_types, savename) {
  p <- ggplot(DT[dwelling_type %in% dwelling_types],
               aes(x = NHouseholds, y = cpd_divided_by_N, colour = dwelling_type)) +
    geom_line(size = 1.2) +
    theme_minimal() +
    scale_y_continuous(breaks = round(seq(0,max(DT$cpd_divided_by_N, na.rm = TRUE), by = 2),0),
                       labels = as.character(round(seq(0,max(DT$cpd_divided_by_N, na.rm = TRUE), by = 2))),
                       limits = c(0,round(max(DT$cpd_divided_by_N),0))) +
    scale_x_continuous(breaks = seq(0,50,5)) +
    scale_colour_manual(values = c(VectorColours$hex[1],
                                   VectorColours$hex[2],
                                   VectorColours$hex[4],
                                   VectorColours$hex[5]))
  p + labs(y = "ADMD (kW)", x = "Number of households", colour = "Dwelling type")
  ggsave(paste0(pPath, 'dwelling_type_comparison/', savename, ".png"))
}

dwelling_types <- c("House (electricity only)", "House (dual fuel)")
compare_household_types(DT_50_labelled, 
                        dwelling_types, 
                        "elec_dual")

dwelling_types <- c("House (old, electricity only)",
                    "House (new, electricity only)")
compare_household_types(DT_50_labelled, dwelling_types, "new_old_elec")

dwelling_types <- c("House (small)", "House (medium)", "House (large)")
compare_household_types(DT_50_labelled, dwelling_types, "house_small_med_large")


p3 <- ggplot(DT_50[dwelling_type %in% c("House (electricity only)", "House (dual fuel)")],
             aes(x = NHouseholds, y = cpd_divided_by_N, colour = dwelling_type)) +
  geom_line(size = 1.2) +
  theme_minimal() +
  scale_y_continuous(breaks = round(seq(0,max(DT_100$cpd_divided_by_N, na.rm = TRUE), by = 2),0)) +
  scale_x_continuous(breaks = seq(0,50,5)) +
  scale_colour_manual(values = VectorColours$hex)
p3 + labs(y = "ADMD (kW)", x = "Number of households", colour = "Dwelling type")
ggsave(paste0(pPath, "elec_dual_comparison.png"))

p4 <- ggplot(DT_50[dwelling_type %in% c("House_Elec", "House_Dual")],
             aes(x = NHouseholds)) +
  geom_line(aes(y = percentile95th), 
            colour = VectorColours$hex[2],
            size = 1.2) +
  geom_line(aes(y = cpd_divided_by_N), 
            colour = VectorColours$hex[1],
            size = 1.2) +
  theme_minimal() +
  scale_y_continuous(breaks = round(seq(0,max(DT_100$cpd_divided_by_N, na.rm = TRUE), by = 2),0)) +
  scale_x_continuous(breaks = seq(0,50,5)) +
  facet_wrap(~dwelling_type, ncol = 1)
p4 + labs(y = "Diversity factor", x = "Number of households", colour = "Dwelling type")

#####################################################
############ Vector's existing equation: ############
#####################################################

DT <- {}
N_cutoff <- 3
epsilon <- c(6.5,7,7.5)
#epsilon_value <- 7
dwelling_type <- all_dwelling_types[12]
for (dwelling_type in all_dwelling_types){
  
  df <- read_csv(paste0(dPathProject, 'diversity_demand_20_iterations_', 
                        dwelling_type, '.csv'))
  dt <- as.data.table(df)
  
#  for (epsilon_value in epsilon){ This was used to visually compare different values
    dt$ADMDn_eq <-
      min(dt$percentile_95th_smoothed) * (1 + epsilon_value /dt$NHouseholds)
    
    # Create large DT of all values
    dt$dwelling_type <- dwelling_type
    DT <- rbind(DT, dt[,.(NHouseholds, percentile_95th_smoothed,ADMDn_eq, dwelling_type)])
  
    # Prepare to plot
    dt_melted <-
      melt(dt[, .(NHouseholds, percentile95th, ADMDn_eq)], 
           id = 'NHouseholds')
    
    dt_melted[variable == 'ADMDn_eq']$variable <- "Calculated (Vector equation)"
    dt_melted[variable == 'percentile95th']$variable <- "Computed from data"
    
    
    # Plot
    p5 <- ggplot(dt_melted, aes(x = NHouseholds, y = value, colour = variable)) +
      geom_line(size = 1.2) +
      theme_bw() +
      scale_y_continuous(limits = c(0, 8.2),
                         breaks =  seq(0, 8, 1)) +
      scale_x_continuous(breaks = seq(0,200,20),
                         limits = c(N_cutoff,200)) +
      scale_colour_manual(values = c(VectorColours$hex[1], 
                                     VectorColours$hex[4],
                                     VectorColours$hex[2])) +
      theme(text = element_text(size = 16), legend.position = "none")
    p5 + labs(y = 'ADMD per ICP (kW)', colour = "", x = "Number of households")
    # p5 + labs(y = 'ADMD per ICP (kW)', colour = "", x = "Number of households",
    #           title = paste0(dwelling_type, " ADMD comparison, epsilon = ", epsilon_value))
    # 
    ggsave(paste0(pPath, "methodology_comparison/Vector_eq_optimisation/", dwelling_type, 
                  "_ADMD_curve_methodology_comparison_epsilon_", epsilon_value, ".png"),
           height = 6, width = 5)
  }
#}

admd_inf <- DT[NHouseholds == 200]

diversity_curve_df <- dt[,.(NHouseholds, ADMDn_eq)]
diversity_curve_df$curve <- (1 + epsilon_value /dt$NHouseholds)
diversity_curve_df$test <- diversity_curve_df$ADMDn_eq/min(diversity_curve_df$ADMDn_eq)

p6 <-
  ggplot(diversity_curve_df[NHouseholds > 3], aes(x = NHouseholds, y = curve)) +
  geom_line(size = 1.2) +
  theme_bw() +
  scale_y_continuous(limits = c(1, 2.8),
                     breaks =  seq(1, 2.8, 0.2)) +
  scale_x_continuous(breaks = seq(0, 200, 20),
                     limits = c(N_cutoff, 200)) +
  scale_colour_manual(values = c(VectorColours$hex[1],
                                 VectorColours$hex[4],
                                 VectorColours$hex[2])) +
  theme(text = element_text(size = 16))
p6 + labs(y = 'Diversity factor', colour = "", x = "Number of households")
ggsave(paste0(pPath, "diversity_factor_curve.png"))

diversity_demand_EV_smart_meter_data <- read_csv("C:/Users/ParkerR/EV-Behaviour-Analysis/data/diversity_demand_2015_smart_meter_data.csv")

df_anytime_max_dem <- diversity_demand_EV_smart_meter_data %>%
  group_by(NHouseholds) %>%
  summarise(meanADMD = mean(ADMD), 
            minADMD = min(ADMD),
            maxADMD = max(ADMD),
            percentile95th = quantile(ADMD, probs = 95/100))
df_anytime_max_dem$percentile_95th_smoothed <-
  loess(percentile95th ~ NHouseholds, data = df_anytime_max_dem, span = 0.3)$fitted

df_anytime_max_dem$Vector_eq_modified <-
  min(df_anytime_max_dem$percentile_95th_smoothed) * (1 + 7 / df_anytime_max_dem$NHouseholds)

gamma <- df_anytime_max_dem$NHouseholds * min(df_anytime_max_dem$percentile_95th_smoothed)
df_anytime_max_dem$Sun_et_el_eq_modified <- 
  (gamma * (1 + 15 /gamma))/df_anytime_max_dem$NHouseholds

p6 <- ggplot(df_anytime_max_dem, aes(x = NHouseholds)) +
  geom_line(aes(y = percentile95th), colour = VectorColours$hex[2], size = 1.2) +
  geom_line(aes(y = Vector_eq_modified), colour = VectorColours$hex[5], size = 1.2) +
  geom_line(aes(y = Sun_et_el_eq_modified), colour = VectorColours$hex[1], size = 1.2) +
  theme_minimal() +
  theme(text = element_text(size = 18))
p6 + labs(y = 'Max demand (kW)', x = "Number of households")
ggsave(paste0(pPath, "anytime_EV_trialists_equation_comparison.png"))


# Check if the original value (3.02) looks better when using mean rather than 95th PC
df_anytime_max_dem$mean_smoothed <-
  loess(meanADMD ~ NHouseholds, data = df_anytime_max_dem, span = 0.3)$fitted
df_anytime_max_dem$Vector_eq_using_mean <-
  min(df_anytime_max_dem$mean_smoothed) * (1 + 3.02 / df_anytime_max_dem$NHouseholds)

gamma <- df_anytime_max_dem$NHouseholds * min(df_anytime_max_dem$mean_smoothed)

p7 <- ggplot(df_anytime_max_dem, aes(x = NHouseholds)) +
  geom_line(aes(y = meanADMD), colour = VectorColours$hex[2], size = 1.2) +
  geom_line(aes(y = Vector_eq_using_mean), colour = VectorColours$hex[5], size = 1.2) +
  theme_minimal() +
  theme(text = element_text(size = 18))
p7 + labs(y = 'Max demand (kW)', x = "Number of households")
ggsave(paste0(pPath, "anytime_EV_trialists_equation_comparison_original_eq_value_and_mean_data.png"))


  