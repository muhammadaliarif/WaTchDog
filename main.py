import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from core.validator import validate
from core.health import calculate_health, get_status, get_first_warning
from core.alerts import send_alert

def load_nasa_data(filepath, unit=1):
    columns = ['unit', 'cycle', 'os1', 'os2', 'os3',
               's1','s2','s3','s4','s5','s6','s7','s8','s9','s10',
               's11','s12','s13','s14','s15','s16','s17','s18','s19','s20','s21']

    df = pd.read_csv(filepath, sep=r'\s+', header=None,
                     names=columns, engine='python')

    df = df[df['unit'] == unit].copy()

    df = df.rename(columns={
        's2': 'temperature_C',
        's11': 'vibration_mm_s'
    })

    return df[['cycle', 'vibration_mm_s', 'temperature_C']]


def plot_results(df, status, warning_cycle, title="WatchDog Health Monitor"):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(df['cycle'], df['vibration_mm_s'],
             color='steelblue', linewidth=0.8, label='Vibration / Fan Speed')
    ax1.set_ylabel('Sensor Reading')
    ax1.legend()
    ax1.set_title(f'{config.PROJECT_NAME} v{config.VERSION} — {title}')

    ax2.plot(df['cycle'], df['health_rolling'],
             color='black', linewidth=1.5, label='Health Score (rolling avg)')
    ax2.axhline(config.WARNING_THRESHOLD, color='orange', linestyle='--',
                linewidth=1.2, label=f'Warning ({config.WARNING_THRESHOLD})')
    ax2.axhline(config.CRITICAL_THRESHOLD, color='red', linestyle='--',
                linewidth=1.2, label=f'Critical ({config.CRITICAL_THRESHOLD})')

    ax2.fill_between(df['cycle'], config.WARNING_THRESHOLD,
                     config.CRITICAL_THRESHOLD, alpha=0.1, color='orange')
    ax2.fill_between(df['cycle'], config.CRITICAL_THRESHOLD,
                     100, alpha=0.1, color='red')

    if warning_cycle is not None:
        ax2.axvline(warning_cycle, color='orange', linestyle=':', linewidth=1.5)
        ax2.annotate(f"Early warning\nCycle {warning_cycle}",
                     xy=(warning_cycle, config.WARNING_THRESHOLD),
                     xytext=(warning_cycle - 40, 70),
                     arrowprops=dict(arrowstyle='->', color='orange'),
                     fontsize=9)

    total_cycles = df['cycle'].max()
    ax2.axvline(total_cycles, color='red', linestyle=':', linewidth=1.5)
    ax2.annotate(f"End of data\nCycle {total_cycles}",
                 xy=(total_cycles, config.CRITICAL_THRESHOLD),
                 xytext=(total_cycles - 50, 90),
                 arrowprops=dict(arrowstyle='->', color='red'),
                 fontsize=9)

    ax2.set_ylabel('Health Score (0-100)')
    ax2.set_xlabel('Operating Cycles')
    ax2.legend()
    ax2.set_ylim(0, 105)

    plt.tight_layout()
    plt.savefig('watchdog_output.png', dpi=150)
    plt.show()


def run(filepath, unit=1):
    print(f"\n{'='*50}")
    print(f"  {config.PROJECT_NAME} v{config.VERSION}")
    print(f"{'='*50}\n")

    # Step 1 - Load data
    print(f"Loading data from {filepath}...")
    df = load_nasa_data(filepath, unit=unit)
    print(f"Loaded {len(df)} cycles for engine {unit}")

    # Step 2 - Validate
    print("\nValidating data...")
    valid, result = validate(df)
    if not valid:
        print(f"VALIDATION FAILED: {result}")
        return
    df = result

    # Step 3 - Calculate health
    print("\nCalculating health score...")
    df = calculate_health(df)

    # Step 4 - Get status
    status = get_status(df)
    warning_cycle = get_first_warning(df)
    total_cycles = df['cycle'].max()

    # Step 5 - Print results
    print(f"\n{'='*50}")
    print(f"  RESULTS — Engine {unit}")
    print(f"{'='*50}")
    print(f"  Total cycles run: {total_cycles}")
    if warning_cycle:
        print(f"  Early warning at: cycle {warning_cycle}")
        print(f"  Warning lead time: {total_cycles - warning_cycle} cycles")
    else:
        print(f"  No warning triggered")
    print(f"  Final health score: {status['score']}/100")
    print(f"  Status: {status['status']}")
    print(f"  {status['message']}")
    print(f"{'='*50}\n")

    # Step 6 - Send alert email
    send_alert(
        status=status['status'],
        score=status['score'],
        cycle=total_cycles,
        machine_name=f"Engine {unit}"
    )

    # Step 7 - Plot
    plot_results(df, status, warning_cycle, title=f"Engine {unit} Analysis")


if __name__ == "__main__":
    run("data/train_FD001.txt", unit=1)