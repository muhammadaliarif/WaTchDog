from flask import Flask, render_template
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.validator import validate
from core.health import calculate_health, get_status, get_first_warning
import pandas as pd
import json

app = Flask(__name__)

def load_and_analyse(unit=1):
    columns = ['unit', 'cycle', 'os1', 'os2', 'os3',
               's1','s2','s3','s4','s5','s6','s7','s8','s9','s10',
               's11','s12','s13','s14','s15','s16','s17','s18','s19','s20','s21']

    df = pd.read_csv('../data/train_FD001.txt', sep=r'\s+', header=None,
                     names=columns, engine='python')

    df = df[df['unit'] == unit].copy()
    df = df.rename(columns={'s2': 'temperature_C', 's11': 'vibration_mm_s'})
    df = df[['cycle', 'vibration_mm_s', 'temperature_C']]

    valid, result = validate(df)
    if not valid:
        return None

    df = result
    df = calculate_health(df)
    status = get_status(df)
    warning_cycle = get_first_warning(df)
    total_cycles = int(df['cycle'].max())

    # Build chart data
    cycles = df['cycle'].tolist()
    health_scores = df['health_rolling'].fillna(0).tolist()
    vibration = df['vibration_mm_s'].tolist()

    lead_time = int(total_cycles - warning_cycle) if warning_cycle else None

    return {
        'status': status['status'],
        'score': status['score'],
        'message': status['message'],
        'total_cycles': total_cycles,
        'warning_cycle': int(warning_cycle) if warning_cycle else None,
        'lead_time': lead_time,
        'cycles': json.dumps(cycles),
        'health_scores': json.dumps(health_scores),
        'vibration': json.dumps(vibration),
        'warning_threshold': config.WARNING_THRESHOLD,
        'critical_threshold': config.CRITICAL_THRESHOLD,
        'machine_name': f'Engine {unit}',
        'version': config.VERSION
    }

@app.route('/')
def index():
    data = load_and_analyse(unit=1)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)