# WatchDog Configuration
# All settings live here — change these without touching any other file

PROJECT_NAME = "WatchDog"
VERSION = "0.1.0"

# Health score thresholds
WARNING_THRESHOLD = 60
CRITICAL_THRESHOLD = 85

# Rolling window size (number of cycles to average)
ROLLING_WINDOW = 10

# Baseline period (first N cycles used to define "normal")
BASELINE_CYCLES = 20

# Sensor weighting (must add up to 1.0)
VIBRATION_WEIGHT = 0.6
TEMPERATURE_WEIGHT = 0.4

# Data folder
DATA_PATH = "data/"