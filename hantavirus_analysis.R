# hantavirus_analysis.R
# Hantavirus Prediction Using Climate Data (1993-2023)

library(tidyverse)
library(MASS)
library(viridis)

# ============================================================
# CONSTANTS
# ============================================================
FOUR_CORNERS <- c("Arizona", "Colorado", "New Mexico", "Utah", "Nevada")
CDC_FILE <- "cdc_hantavirus_1993_2023.csv"
WEATHER_FILE <- "4328282.csv"
RAW_CDC_FILE <- "raw_cdc_data.txt"

# ============================================================
# GENERATE CDC CSV FROM RAW TEXT
# ============================================================
generate_cdc_csv <- function() {
  if (!file.exists(RAW_CDC_FILE)) {
    stop(paste("Error:", RAW_CDC_FILE, "not found"))
  }
  
  text <- read_file(RAW_CDC_FILE)
  splits <- str_split(text, "Table of U\\.S\\. Hantavirus Cases by (\\d{4}) \\(All States\\)")[[1]]
  
  data <- tibble()
  
  for (i in seq(2, length(splits), by = 2)) {
    year <- as.integer(splits[i])
    lines <- str_split(splits[i + 1], "\n")[[1]]
    
    for (line in lines) {
      nums <- str_extract_all(line, "\\d+")[[1]]
      if (length(nums) >= 4) {
        state_name <- trimws(str_split(line, "\\d+")[[1]][1])
        if (nchar(state_name) > 0 && !(state_name %in% c("State", "Total", "Year", "Month"))) {
          data <- bind_rows(data, tibble(
            year = year,
            state = state_name,
            cases = as.integer(nums[length(nums)])
          ))
        }
      }
    }
  }
  
  write_csv(data, CDC_FILE)
  cat("✅ Created", CDC_FILE, "with", nrow(data), "records\n")
  return(TRUE)
}

# ============================================================
# LOAD AND PROCESS DATA
# ============================================================
load_and_process_data <- function() {
  # CDC data
  cdc <- read_csv(CDC_FILE, show_col_types = FALSE) %>%
    filter(state %in% FOUR_CORNERS)
  
  # Weather data
  weather <- read_csv(WEATHER_FILE, col_types = cols(.default = col_character())) %>%
    mutate(
      year = as.integer(str_sub(DATE, 1, 4)),
      PRCP = as.numeric(PRCP),
      TAVG = as.numeric(TAVG)
    ) %>%
    group_by(year) %>%
    summarise(
      PRCP = sum(PRCP, na.rm = TRUE),
      TAVG = mean(TAVG, na.rm = TRUE),
      .groups = "drop"
    )
  
  # Merge and create lags
  merged <- cdc %>%
    inner_join(weather, by = "year") %>%
    arrange(state, year) %>%
    group_by(state) %>%
    mutate(
      precip_lag_12 = lag(PRCP, 1),
      temp_lag_12 = lag(TAVG, 1)
    ) %>%
    ungroup() %>%
    drop_na()
  
  return(merged)
}

# ============================================================
# RUN MODELS AND GENERATE GRAPHS
# ============================================================
run_models_and_generate_graphs <- function(df) {
  # Fit models
  model_p <- glm.nb(cases ~ precip_lag_12, data = df)
  model_t <- glm.nb(cases ~ temp_lag_12, data = df)
  
  # --- GRAPH 1: AIC COMPARISON ---
  aic_df <- tibble(
    model = c("Precipitation\n(1-Year Lag)", "Temperature\n(1-Year Lag)"),
    aic = c(AIC(model_p), AIC(model_t)),
    color = c("#3498db", "#e74c3c")
  )
  
  p1 <- ggplot(aic_df, aes(x = model, y = aic, fill = model)) +
    geom_col(alpha = 0.85, color = "black", linewidth = 0.8) +
    geom_text(aes(label = round(aic, 2)), vjust = -0.5, size = 5, fontface = "bold") +
    scale_fill_manual(values = c("#3498db", "#e74c3c"), guide = "none") +
    labs(
      title = "Model Comparison: Predicting Hantavirus in the Four Corners",
      y = "AIC Score (Lower is Better)",
      x = NULL
    ) +
    theme_minimal(base_size = 14) +
    theme(
      plot.title = element_text(face = "bold", size = 14),
      axis.text = element_text(size = 12),
      axis.title.y = element_text(face = "bold", size = 12)
    ) +
    ylim(0, max(aic_df$aic) * 1.05)
  
  ggsave("final_aic_comparison.png", p1, width = 8, height = 5, dpi = 300)
  cat("✅ Saved 'final_aic_comparison.png'\n")
  
  # --- GRAPH 2: CORRELATION HEATMAP ---
  corr_cols <- df %>% dplyr::select(cases, PRCP, TAVG, precip_lag_12, temp_lag_12)
  colnames(corr_cols) <- c("Hanta Cases", "Current Rain", "Current Temp", "Rain (1 Yr Lag)", "Temp (1 Yr Lag)")
  
  corr_matrix <- cor(corr_cols)
  
  # Reshape for ggplot
  corr_long <- as.data.frame(corr_matrix) %>%
    mutate(var1 = rownames(corr_matrix)) %>%
    pivot_longer(-var1, names_to = "var2", values_to = "corr")
  
  p2 <- ggplot(corr_long, aes(x = var1, y = var2, fill = corr)) +
    geom_tile(color = "black", linewidth = 0.8) +
    geom_text(aes(label = round(corr, 3)), size = 4.5, color = "black") +
    scale_fill_gradient2(
      low = "#2166ac", mid = "#f7f7f7", high = "#b2182b",
      midpoint = 0, limits = c(-0.2, 0.5),
      name = "Correlation"
    ) +
    labs(
      title = "Correlation Matrix: Climate Variables vs. Hantavirus Cases",
      x = NULL, y = NULL
    ) +
    theme_minimal(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", size = 13),
      axis.text.x = element_text(angle = 45, hjust = 1, size = 10),
      axis.text.y = element_text(size = 10),
      legend.position = "right"
    )
  
  ggsave("final_correlation_heatmap.png", p2, width = 8, height = 6, dpi = 300)
  cat("✅ Saved 'final_correlation_heatmap.png'\n")
  
  # Print summary
  cat("\n", strrep("=", 60), "\n", sep = "")
  cat("MODEL RESULTS SUMMARY\n")
  cat(strrep("=", 60), "\n\n", sep = "")
  cat(sprintf("Precipitation Model AIC: %.2f\n", AIC(model_p)))
  cat(sprintf("Temperature Model AIC:   %.2f\n", AIC(model_t)))
  
  best <- ifelse(AIC(model_p) < AIC(model_t), "Precipitation", "Temperature")
  cat(sprintf("\nBest model: %s\n", best))
  
  irr <- exp(coef(model_p)["precip_lag_12"])
  pct_increase <- (irr - 1) * 100
  cat(sprintf("IRR: %.4f\n", irr))
  cat(sprintf("(Each additional inch of precipitation → %.1f%% increase in expected cases)\n", pct_increase))
}

# ============================================================
# MAIN
# ============================================================
main <- function(generate_csv = FALSE, skip_csv_check = FALSE) {
  cat(strrep("=", 60), "\n", sep = "")
  cat("HANTAVIRUS PREDICTION ANALYSIS\n")
  cat(strrep("=", 60), "\n\n", sep = "")
  
  if (generate_csv) {
    generate_cdc_csv()
  }
  
  if (!skip_csv_check && !file.exists(CDC_FILE)) {
    cat(sprintf("\n❌ Error: %s not found\n", CDC_FILE))
    if (file.exists(RAW_CDC_FILE)) {
      cat("Run with generate_csv = TRUE to create it from raw data\n")
    }
    return(invisible(NULL))
  }
  
  cat("Loading and processing data...\n")
  merged_df <- load_and_process_data()
  cat(sprintf("✅ Data loaded: %d records\n\n", nrow(merged_df)))
  
  cat("Running models and generating graphs...\n")
  run_models_and_generate_graphs(merged_df)
  
  cat("\n🎉 Analysis complete! Check your folder for the graph files.\n")
}

# ============================================================
# RUN
# ============================================================
# Change these as needed:
main(generate_csv = FALSE, skip_csv_check = FALSE)