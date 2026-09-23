import numpy as np
from pyspark.sql import functions as F
from pyspark.sql import types as T

@F.udf(T.IntegerType())
def binomial_udf(n):
    if n is None:
        return None
    return int(np.random.binomial(n, 0.5))

def get_random_sample(df_tot, column='weight'):
    # Paso 1: Redondear hacia arriba
    df = df_tot.withColumn("W", F.ceil(F.col(column).cast("double")))

    # Paso 2: Aplicar binomial real
    df = df.withColumn("w1", binomial_udf(F.col("W"))) \
           .withColumn("w2", F.col("W") - F.col("w1"))

    # Paso 3: Crear dos DataFrames de salida
    df_1 = df.drop("W", "w2").withColumn(column, F.col("w1")).drop("w1")
    df_2 = df.drop("W", "w1").withColumn(column, F.col("w2")).drop("w2")

    return df_1, df_2


def mapping_for_embedding(df):
    nodes_O = df.select(F.col('origen').alias('node'))
    nodes_D = df.select(F.col('destino').alias('node'))

    nodes = nodes_O.union(nodes_D).distinct()

    nodes_dict = {row['node']: idx for idx, row in enumerate(nodes.collect())}

    # Mapping values to indexes
    def map_to_index(value):
        return nodes_dict.get(value, 0)  # Return '0' if it is not in the dict

    map_udf = F.udf(map_to_index, T.IntegerType())

    # Add two new columns with the index of the zones   
    df = df.withColumn('origin_id', map_udf('origen')).withColumn('destination_id', map_udf('destino'))

    return df, nodes_dict
