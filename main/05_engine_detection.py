# Airplane Engine Detection
# Detect Airplane Engine from FDM Data. Engine are identified using these columns:
# 1. `engcycle_x_hr`: If exist `engcycle_4_hr` column value, then airplane has 4 engine.
# 2. `ctrlcolumn_pos_capt`: If exist `ctrlcolumn_pos_capt` column value, then airplane engine is B747, otherwise it's A380.

### Import
import math
import numpy as np
import pandas as pd
import seaborn as sns
import multiprocessing as mp
import os

### Functions
#### 1. Create Helper Function to Detect Engine
def identify_engine(filepath):
    fdm_df = pd.read_csv(filepath)
    engine = None
    sum_engcycle_4_hr = fdm_df['engcycle_4_hr'].sum()
    sum_pos_capt = fdm_df['ctrlcolumn_pos_capt'].sum()
    sum_pos_fo = fdm_df['ctrlcolumn_pos_fo'].sum()
    if fdm_df['engcycle_4_hr'].sum() > 0:
        if sum_pos_capt > 0 and sum_pos_fo > 0:
            engine = 'B747'
        else:
            engine = 'A380'
    row_str = ','.join([os.path.basename(filepath), str(sum_engcycle_4_hr), str(sum_pos_capt), str(sum_pos_fo), engine])
    print(row_str)
    return row_str

## Main
if __name__ == "__main__":

    base_path = '../dataset/database_local'
    # base_path = '../dataset/database'

    #### 1. Read Flight Runway Data 
    flight_runway_file = f'{base_path}/04_flights_with_runway.csv'
    flight_runway = pd.read_csv(flight_runway_file)

    #### 2. Read Landing Runway Count
    landing_runway_file = f'{base_path}/04_landing_count_detail.csv'
    landing_runway_count = pd.read_csv(landing_runway_file)

    ## Transform Data 
    #### 1. Append Full Runway Id Column
    arrival_runway_id = flight_runway['arr_airport'] + '.' + flight_runway['arr_rwy']
    flight_runway['arr_rwy_id'] = arrival_runway_id

    #### 2. Select Flight with Selected Runway Id
    # landing_runways = ['MSP.30R', 'DTW.03L']
    landing_runways = ['MSP.30R']
    selected_flight = flight_runway[flight_runway['arr_rwy_id'].isin(landing_runways)]

    #### 4. Determine Engine

    # Export Header to CSV
    output_file = f'{base_path}/05_flight_engine.csv'
    csv_header = ['filepath', 'sum_engcycle_4_hr', 'sum_pos_capt', 'sum_pos_fo', 'engine']

    file = open(output_file, "w")
    L = ','.join(csv_header) + '\n'
    file.writelines(L)
    file.close()

    # Multiprocessing
    params = selected_flight.fullpath.tolist()
    p = mp.Pool(10)
    with open(output_file, 'a') as f:
        for result in p.imap_unordered(identify_engine, params):
            f.write('%s\n' % result)