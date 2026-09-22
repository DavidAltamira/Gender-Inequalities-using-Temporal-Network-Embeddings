import numpy as np

def lorenz_hotspots(df, col_value="closeness"):
    hotspots = df.sort_values(by=col_value, ascending=True).dropna(subset=[col_value]).reset_index()#drop=True)
    total_accessibility = hotspots[col_value].sum()
    hotspots["cum_accessibility"] = hotspots[col_value].cumsum()
    hotspots["cum_share"] = hotspots["cum_accessibility"] / total_accessibility

    x = np.linspace(0, 1, len(hotspots))
    dL = np.gradient(hotspots["cum_share"], x)
    slope_end = dL[-1]
    threshold = 1 - 1 / slope_end
    
    return hotspots, threshold

def iterative_lorenz_hotspots(gdf, value_col="closeness", n_iter=3, comparable_cutoff=None):
    remaining = gdf.copy()
    hotspot_sets = []
    hotspots_level = gdf.copy()
    hotspots_level["hotspot_level"] = 0

    for level in range(1, n_iter + 1):
        if len(remaining) < 5:
            break

        lorenz_df, threshold = lorenz_hotspots(remaining, col_value=value_col)

        if comparable_cutoff is None:
            cutoff = int(threshold * len(lorenz_df))
        else:
            cutoff = comparable_cutoff[level-1]['cutoff']

        hot_nodes = lorenz_df.iloc[cutoff:]
        original_idx = hot_nodes['index']

        hotspots_level.loc[original_idx, "hotspot_level"] = level

        hotspot_sets.append({"level": level, "threshold": threshold, "cutoff": cutoff, "n_removed": len(hot_nodes)})

        remaining = remaining.loc[~remaining.index.isin(original_idx)]

    return hotspots_level, hotspot_sets