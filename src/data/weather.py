import numpy as np
import pandas as pd
import meteostat as ms 

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c


def idw_weights(distances, power=2):
    distances = np.where(distances == 0, 1e-10, distances)
    weights = 1 / distances**power
    return weights / weights.sum()


def get_weather_data_ByNode(nodeID, start, end, all_nodes, k=4, power=2):

    lat = nodeID['lat']
    lon = nodeID['lon']
    
    point_i = ms.Point(lat, lon)
    data_i = ms.Daily(point_i, start, end).fetch()
    
    # If data exist → return the original
    if not data_i.empty:
        data_i = data_i.reset_index()
        data_i['ID'] = nodeID['ID']
        return data_i
    
    neighbor_data = []
    distances = []

    for other in all_nodes:
        if other['ID'] == nodeID['ID']:
            continue
        
        point_j = ms.Point(other['lat'], other['lon'])
        data_j = ms.Daily(point_j, start, end).fetch()
        
        if not data_j.empty:
            data_j = data_j.reset_index()
            data_j['node'] = other['ID']
            
            neighbor_data.append(data_j)
            
            d = haversine(lat, lon, other['lat'], other['lon'])
            distances.append(d)
    
    if len(neighbor_data) == 0:
        return pd.DataFrame()
    
    # Take closest k
    distances = np.array(distances)
    idx_sorted = np.argsort(distances)[:k]
    
    selected_data = [neighbor_data[i] for i in idx_sorted]
    selected_distances = distances[idx_sorted]
    
    weights = idw_weights(selected_distances, power=power)
    
    combined = pd.concat(selected_data)
    meteo_cols = combined.columns.drop(['time', 'node'])
    
    interpolated = []
    
    for date, group in combined.groupby('time'):
        row_vals = []
        
        for col in meteo_cols:
            vals = group[col].values
            
            if len(vals) == len(weights):
                row_vals.append(np.sum(vals * weights))
            else:
                row_vals.append(np.nan)
        
        interpolated.append([date] + row_vals)
    
    result = pd.DataFrame(interpolated, columns=['time'] + list(meteo_cols))
    result['ID'] = nodeID['ID']
    
    return result