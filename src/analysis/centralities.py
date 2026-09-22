import ast
import pandas as pd
import networkx as nx

def compute_centralities(G, weight='weight'):

    # Invert the weigths
    G_inverted_weights = G.copy()
    for u, v, d in G_inverted_weights.edges(data=True):
        if d['weight'] > 0:
            d['weight'] = 1.0 / d['weight']
        else:
            d['weight'] = float('inf')


    in_strength = dict(G.in_degree(weight=weight))
    out_strength = dict(G.out_degree(weight=weight))
    strength = {n: in_strength.get(n, 0) + out_strength.get(n, 0) for n in G.nodes()}
    
    betweenness = nx.betweenness_centrality(G_inverted_weights, weight=weight)

    closeness = nx.closeness_centrality(G_inverted_weights, distance=weight)

    return {
        'strength': strength,
        'betweenness': betweenness,
        'closeness': closeness
    }


def get_ratio_matrix_for_centralities(df_centralities, net_metric='closeness'):
    df_centralities['day'] = pd.to_datetime(df_centralities['day'], format='%Y%m%d')
    df_centralities = df_centralities.sort_values(by='day').reset_index(drop=True)
    centralities_men = df_centralities[df_centralities.gender == 'hombre'].reset_index(drop=True)
    centralities_women = df_centralities[df_centralities.gender == 'mujer'].reset_index(drop=True)

    net_metric_men = pd.DataFrame.from_records(centralities_men[net_metric].apply(ast.literal_eval))
    net_metric_women = pd.DataFrame.from_records(centralities_women[net_metric].apply(ast.literal_eval))

    daily_metric_men = pd.concat([centralities_men[['day']].reset_index(drop=True), net_metric_men], axis=1)
    daily_metric_women = pd.concat([centralities_women[['day']].reset_index(drop=True), net_metric_women], axis=1)

    daily_metric_men_panel = daily_metric_men.set_index('day')
    daily_metric_women_panel = daily_metric_women.set_index('day')

    daily_metric_ratio = daily_metric_women_panel / daily_metric_men_panel

    if daily_metric_ratio.isna().any().any():
        daily_metric_ratio = daily_metric_ratio.dropna(axis=1)

    return daily_metric_ratio, daily_metric_women_panel, daily_metric_men_panel


def find_top_bottom_quartile_districts(df, low_quartile=0.10, top_quartile=0.90, threshold_persistance = 0.75, value_name='closeness'):
    """
    df should be a matrix with 'days' in the rows and the 'districts' for each column. The values are the 'value_name'
    """

    ### PART 1: count how many days the nodes appear in the low or top quartile ###
    df_long = df.melt(id_vars='day', var_name='district', value_name=value_name)
    #df_long['district'] = df_long['district'].map(dict_SC_inv)

    p_low = df_long["closeness"].quantile(low_quartile)
    p_top = df_long["closeness"].quantile(top_quartile)

    df_long["group"] = "middle"
    df_long.loc[df_long["closeness"] <= p_low, "group"] = "low"
    df_long.loc[df_long["closeness"] >= p_top, "group"] = "high"

    extreme_counts = (
        df_long[df_long["group"] != "middle"]
        .groupby(["district","group"])
        .size()
        .unstack(fill_value=0)
    )

    ### PART 2: filter the nodes that appears 60% (threshold_persistance) of times on those quartiles

    districts_low_q = list(extreme_counts[((extreme_counts["low"] / len(df)) > threshold_persistance)].reset_index()['district'])
    districts_high_q = list(extreme_counts[((extreme_counts["high"] / len(df)) > threshold_persistance)].reset_index()['district'])

    return districts_low_q, districts_high_q, extreme_counts


def map_closeness(G, gdf):
    # Invert the weight
    for u, v, d in G.edges(data=True):
        d['dist'] = 1 / d['flow'] if d['flow'] != 0 else 0

    # Compute the closeness & order in a df
    closeness = nx.closeness_centrality(G, distance='dist')
    closeness_df = pd.DataFrame.from_dict(closeness, orient='index', columns=['closeness'])
    closeness_df.reset_index(inplace=True)
    closeness_df.rename(columns={'index': 'node'}, inplace=True)

    # Merge with geopandas df
    gdf_syn = gdf.merge(closeness_df, left_on='ID', right_on='node', how='left')

    return gdf_syn