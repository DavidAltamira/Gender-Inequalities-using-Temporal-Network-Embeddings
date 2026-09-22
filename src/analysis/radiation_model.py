import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import haversine_distances

EARTH_RADIUS_KM = 6371.0

def radiation_model(df: pd.DataFrame):

    coords = np.radians(df[['lat', 'lon']].values)
    populations = df['population'].values
    outflows = df['tot_outflow'].values
    n = len(df)

    dist_matrix = haversine_distances(coords) * EARTH_RADIUS_KM
    M = populations.sum()

    results = []

    for i in range(n):

        Ti = outflows[i]
        mi = populations[i]

        if Ti <= 0:
            continue

        normalization_factor = 1.0 / (1.0 - mi / M)

        for j in range(n):

            if i == j:
                continue

            mj = populations[j]
            dij = dist_matrix[i, j]

            # s_ij: population inside the radius d_ij (excluding i y j)
            mask = (dist_matrix[i] < dij) & (np.arange(n) != i) & (np.arange(n) != j)
            s_ij = populations[mask].sum()

            Tij = Ti * normalization_factor * (mi * mj) / ((mi + s_ij) * (mi + mj + s_ij))

            results.append((df.iloc[i].tile_id, df.iloc[j].tile_id, Ti, Tij))

    return pd.DataFrame(results, columns=["origin", "destination", "T_i", "flow"])


def common_part_of_commuters(values1, values2):
    """
    Compute the common part of commuters for two pairs of fluxes.

    :param values1: the values for the first array
    :type values1: numpy array

    :param values2: the values for the second array
    :type values1: numpy array

    :return: float
        the common part of commuters
    """
    return 2.0 * np.sum(np.minimum(values1, values2)) / (np.sum(values1) + np.sum(values2))