import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def calculate_health(df):
    """
    Takes a validated dataframe and returns it with health score columns added.
    Uses a rolling baseline instead of hardcoded max values.
    """

    # Step 1 — establish baseline from first N cycles
    baseline = df.head(config.BASELINE_CYCLES)
    
    VIB_NORMAL = baseline['vibration_mm_s'].mean()
    TEMP_NORMAL = baseline['temperature_C'].mean()
    
    # Step 2 — set critical as 3x the baseline variation (standard deviation)
    VIB_STD = baseline['vibration_mm_s'].std()
    TEMP_STD = baseline['temperature_C'].std()
    
    VIB_CRITICAL = VIB_NORMAL + (VIB_STD * 3)
    TEMP_CRITICAL = TEMP_NORMAL + (TEMP_STD * 3)

    print(f"Baseline established from first {config.BASELINE_CYCLES} cycles")
    print(f"Normal vibration: {VIB_NORMAL:.2f}, Critical: {VIB_CRITICAL:.2f}")
    print(f"Normal temperature: {TEMP_NORMAL:.2f}, Critical: {TEMP_CRITICAL:.2f}")

    # Step 3 — calculate scores
    vib_score = ((df['vibration_mm_s'] - VIB_NORMAL) /
                 (VIB_CRITICAL - VIB_NORMAL) * 100).clip(0, 100)

    temp_score = ((df['temperature_C'] - TEMP_NORMAL) /
                  (TEMP_CRITICAL - TEMP_NORMAL) * 100).clip(0, 100)

    # Step 4 — weighted health score
    df['health_score'] = (vib_score * config.VIBRATION_WEIGHT +
                          temp_score * config.TEMPERATURE_WEIGHT)

    # Step 5 — rolling average to smooth noise
    df['health_rolling'] = df['health_score'].rolling(
        window=config.ROLLING_WINDOW).mean()

    # Step 6 — flag alerts
    df['alert'] = df['health_rolling'] > config.WARNING_THRESHOLD

    return df

def get_status(df):
    """
    Returns the current status of the equipment based on latest health score.
    """
    latest = df['health_rolling'].dropna().iloc[-1]

    if latest >= config.CRITICAL_THRESHOLD:
        status = "CRITICAL"
        message = "Immediate maintenance required."
    elif latest >= config.WARNING_THRESHOLD:
        status = "WARNING"
        message = "Equipment degradation detected. Schedule maintenance."
    else:
        status = "NORMAL"
        message = "Equipment operating normally."

    return {
        'status': status,
        'message': message,
        'score': round(latest, 1)
    }

def get_first_warning(df):
    """
    Returns the first cycle where the warning triggered, or None if no warning.
    """
    alerts = df[df['alert']]
    if len(alerts) == 0:
        return None
    return alerts.iloc[0]['cycle']