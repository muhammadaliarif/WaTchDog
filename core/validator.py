import pandas as pd

REQUIRED_COLUMNS = ['cycle', 'vibration_mm_s', 'temperature_C']

def validate(df):
    """
    Takes a dataframe and checks if it's clean enough to use.
    Returns (True, df) if valid, (False, error message) if not.
    """
    
    # Check required columns exist
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return False, f"Missing columns: {missing}"
    
    # Check there's actually data
    if len(df) == 0:
        return False, "Dataset is empty"
    
    # Check for minimum cycles needed
    if len(df) < 20:
        return False, f"Not enough data — need at least 20 cycles, got {len(df)}"
    
    # Check for missing values
    nulls = df[REQUIRED_COLUMNS].isnull().sum()
    if nulls.any():
        print(f"Warning: found missing values, filling with forward fill")
        df[REQUIRED_COLUMNS] = df[REQUIRED_COLUMNS].fillna(method='ffill')
    
    # Check for negative values in vibration
    if (df['vibration_mm_s'] < 0).any():
        return False, "Invalid data — negative vibration values found"
    
    print(f"Data validation passed — {len(df)} cycles loaded")
    return True, df