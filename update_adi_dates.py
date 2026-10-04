#!/usr/bin/env python3
"""
Actualiza los archivos ADI para que cada QSO tenga fecha y hora únicas.
"""

import re
from pathlib import Path

# Configuración: cada actividad en un día distinto de Septiembre 2024
ACTIVITY_DATES = {
    'qsl1': '20240901',
    'qsl2': '20240902',
    'qsl3': '20240903',
    'qsl4': '20240904',
    'qsl5': '20240905',
    'qsl6': '20240906',
    'qsl7': '20240907',
}

# Hora base por actividad (en minutos desde 00:00)
BASE_TIMES = {
    'qsl1': 600,   # 10:00
    'qsl2': 660,   # 11:00
    'qsl3': 720,   # 12:00
    'qsl4': 780,   # 13:00
    'qsl5': 840,   # 14:00
    'qsl6': 900,   # 15:00
    'qsl7': 960,   # 16:00
}

def minutes_to_hhmmss(m):
    h = m // 60
    m = m % 60
    return f"{h:02d}{m:02d}00"

def update_adi_file(filepath, activity, qso_counter):
    """Actualiza un archivo ADI con fechas/horas únicas."""
    content = Path(filepath).read_text(encoding='utf-8')
    
    # Patrón para encontrar cada QSO (entre <QSO_DATE> y <eor>)
    # Reemplazamos QSO_DATE y TIME_ON secuencialmente
    lines = content.split('\n')
    new_lines = []
    in_qso = False
    current_qso = 0
    
    for line in lines:
        # Detectar inicio de QSO (línea con QSO_DATE o CALL)
        if '<QSO_DATE' in line or ('<CALL' in line and not in_qso):
            in_qso = True
            current_qso = qso_counter[0]
            qso_counter[0] += 1
            
            # Calcular fecha y hora única para este QSO
            base_minutes = BASE_TIMES[activity]
            qso_minutes = base_minutes + (current_qso * 5)  # 5 min entre QSOs
            date_str = ACTIVITY_DATES[activity]
            time_str = minutes_to_hhmmss(qso_minutes)
            
            # Reemplazar o insertar QSO_DATE
            if '<QSO_DATE' in line:
                line = re.sub(r'<QSO_DATE:\d+>[^<]*', f'<QSO_DATE:8>{date_str}', line)
            # Reemplazar o insertar TIME_ON
            if '<TIME_ON' in line:
                line = re.sub(r'<TIME_ON:\d+>[^<]*', f'<TIME_ON:6>{time_str}', line)
        
        # Si la línea tiene TIME_ON pero no QSO_DATE en la misma, actualizar TIME_ON
        elif '<TIME_ON' in line and in_qso:
            base_minutes = BASE_TIMES[activity]
            qso_minutes = base_minutes + ((current_qso - 1) * 5)
            time_str = minutes_to_hhmmss(qso_minutes)
            line = re.sub(r'<TIME_ON:\d+>[^<]*', f'<TIME_ON:6>{time_str}', line)
        
        # Detectar fin de QSO
        if '<eor>' in line:
            in_qso = False
        
        new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    Path(filepath).write_text(new_content, encoding='utf-8')
    return qso_counter[0] - 1

def main():
    base = Path('/Users/danielcialdella/Downloads/ia-qsls')
    
    for activity in ['qsl1', 'qsl2', 'qsl3', 'qsl4', 'qsl5', 'qsl6', 'qsl7']:
        folder = base / activity
        adi_files = sorted(folder.glob('*.adi'))
        
        qso_counter = [0]
        for adi_file in adi_files:
            count = update_adi_file(adi_file, activity, qso_counter)
            print(f"{adi_file.name}: {count+1} QSOs actualizados")

if __name__ == '__main__':
    main()