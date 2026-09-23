import numpy as np
import pandas as pd


def day_type(day):
    date = pd.to_datetime(str(day))
    if date.weekday() < 5:
        return "weekday"
    else:
        return "weekend"
    
def get_daily_gdf_colormap(df, day, baselines, gdf_SC):
    df_day = df[df['fecha'] == day]
    
    gdf_colormap = gdf_SC.merge(df_day, left_on='ID', right_on='destino', how='left')
    gdf_colormap["total_trips"] = gdf_colormap["total_trips"].fillna(0)

    date = pd.to_datetime(str(day)).weekday()
    if date == 0:
        df_baseline = baselines[0]
    elif date == 1:
        df_baseline = baselines[1]
    elif date == 2:
        df_baseline = baselines[2]
    elif date == 3:
        df_baseline = baselines[3]
    elif date == 4:
        df_baseline = baselines[4]
    elif date == 5:
        df_baseline = baselines[5]
    else:
        df_baseline = baselines[6]
        
    gdf_colormap = gdf_colormap.merge(df_baseline[['destino', 'baseline_trips']], left_on='ID', right_on='destino', how='left')
    gdf_colormap["baseline_trips"] = gdf_colormap["baseline_trips"].fillna(0)
    
    gdf_colormap["rel_diff"] = np.where(gdf_colormap["baseline_trips"] > 0, 
                                        ((gdf_colormap["total_trips"] - gdf_colormap["baseline_trips"]) / gdf_colormap["baseline_trips"]) * 100, 0)

    return gdf_colormap