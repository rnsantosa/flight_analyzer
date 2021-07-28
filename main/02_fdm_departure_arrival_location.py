import numpy as np
import multiprocessing as mp
import gc
import os
import pandas as pd
import seaborn as sns


# Helper Functions
def get_first_loc(fdm_df):
    # Given FDM Dataframe, get location (lat, lon) from first row
    if fdm_df.empty:
        return (np.nan, np.nan)
    else:
        return tuple(fdm_df[['lat_rad', 'lon_rad']].iloc[0])

def get_last_loc(fdm_df):
    # Given FDM Dataframe, get location (lat, lon) from last row
    if fdm_df.empty:
        return (np.nan, np.nan)
    else:
        return tuple(fdm_df[['lat_rad', 'lon_rad']].iloc[-1])

def get_departure_loc(fdm):
    # Given fdm dataframe, return the departure long lat and arrival long lat
    plane_in_ground   = fdm[fdm['wow'] == 0]
    plane_off_ground  = fdm[fdm['wow'] == 1]
        
    if plane_in_ground.empty:
        return (np.nan, np.nan)

    if plane_off_ground.empty:
        est_departure_loc = tuple(plane_in_ground[['lat_rad', 'lon_rad']].iloc[0])
        return est_departure_loc
    else:
        first_takeoff_idx = plane_off_ground.index[0]
        departure_df = plane_in_ground.loc[:first_takeoff_idx]
        est_departure_loc = get_first_loc(departure_df)
        return est_departure_loc

def get_arrival_loc(fdm):
    # Given fdm dataframe, return the departure long lat and arrival long lat
    plane_in_ground   = fdm[fdm['wow'] == 0]
    plane_off_ground  = fdm[fdm['wow'] == 1]
        
    if plane_in_ground.empty:
        return (np.nan, np.nan)

    if plane_off_ground.empty:
        return (np.nan, np.nan)
    else:
        first_takeoff_idx = plane_off_ground.index[0]
        arrival_df = plane_in_ground.loc[first_takeoff_idx:]
        est_arrival_loc = get_last_loc(arrival_df)
        return est_arrival_loc

def get_loc_from_fdm(fdm_filepath):
    # Given filepath, return row string of df
    fdm_df = pd.read_csv(fdm_filepath)
    fdm_df = fdm_df[(fdm_df['lat_rad'] != 0) & (fdm_df['lon_rad'] != 0)]
    dep_lat, dep_lon, arr_lat, arr_lon = get_departure_loc(fdm_df) + get_arrival_loc(fdm_df)
    
    row = (os.path.basename(fdm_filepath), dep_lat, dep_lon, arr_lat, arr_lon)
    row_str = ",".join(str(r) for r in row)
    
    print(os.path.basename(fdm_filepath))
    return row_str

if __name__ == "__main__":
    # Read FDM Data
    fdm_database_path = '../dataset/database/01_fdm_files.csv'
    fdm_files = pd.read_csv(fdm_database_path)
    
    # Init Create CSV File
    loc_columns = ['dep_lat', 'dep_lon', 'arr_lat', 'arr_lon']
    csv_header = ['fname'] + loc_columns
    output_file = "../dataset/database/02_fdm_location.csv"
    
    file1 = open(output_file, "w")
    L = ','.join(csv_header) + '\n'
    file1.writelines(L)
    file1.close()

    params = fdm_files.fullpath.tolist()
    p = mp.Pool(10)
    with open(output_file, 'a') as f:
        for result in p.imap_unordered(get_loc_from_fdm, params):
            f.write('%s\n' % result)