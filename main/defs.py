import numpy as np
import pandas as pd
import os

cols = ['flap_te_pos', 'hbaro_m', 'hralt_m', 'hdot_1_mps', 'gs_mps', \
        'gs_dev_ddm', 'loc_dev_ddm', 'n11_rpm', 'n12_rpm', 'n13_rpm', \
        'n14_rpm', 'tas_mps', 'theta_rad', 'chi_rad', 'lg_squat_mr']

def get_crucial_df(df_fdm, alt_m, duration_s, sampling_rate=16):
    idx_max = np.where(df_fdm['hbaro_m'].eq(max(df_fdm['hbaro_m'])), df_fdm.index, 0).max()+1
    landing_df = df_fdm.loc[idx_max:]
    crucial_alt_start_idx = landing_df[landing_df['hbaro_m'] <= alt_m].index[0]
    crucial_df = landing_df.loc[crucial_alt_start_idx:].iloc[:duration_s*sampling_rate]
    return crucial_df

def get_crucial_df_from_file(filepath, cols=cols):
    df_fdm = pd.read_csv(filepath, usecols=cols)
    try:
        crucial_df = get_crucial_df(df_fdm, 1000, 10)
    except:
        crucial_df = pd.DataFrame(columns=cols)
    crucial_df['file'] = os.path.basename(filepath)
    return crucial_df