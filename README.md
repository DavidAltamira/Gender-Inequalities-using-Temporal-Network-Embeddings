# Gender Inequalities using temporal-network embeddings
The current project performs an analysis on gender inequalities in urban mobility during the flood of Valencia in 2024, making emphasis on the network connectivity.

## Dataset
The [data set](https://www.transportes.gob.es/ministerio/proyectos-singulares/estudios-de-movilidad-con-big-data/opendata-movilidad) was obtained from the Spanish Ministry of Transport and Mobility. For our purposes, the daily files of trips by districts were used - `mitma-movilidad-v2/estudios_basicos/por-distritos/viajes/ficheros-diarios`.

## Preprocessing and Analysis
To obtain the full dataset you can do it directly from the previous link. However, for efficient procedure in the folder [`data/data_refined`](./data/data_refined/) you can find the data after the pre-processing part, namely the trips inside the Valencian Community during September and December of 2024 and aggregated by gender.

In `data`, you can also find other `*.csv` files with the results of the analysis using the refined data:
- actual_distance_and_node_contribution_last.csv: metrics of the embedding distance by day and the contribution of each node.
- centralities.csv: daily computation of the centralities - betweenness, closeness, and strength.
- centralities_by_gender.csv: daily computation of the centralities - betweenness, closeness, and strength - by gender.
- gender_flows_peak.csv: flow of trips by gender during the peak day (30/10/2024).
- gender_flows_typical.csv: flow of trips by gender a typical day. For more robust analysis, the typical day was chosen as the average of 4 days - 02, 09, 16 and 23 - of October, 2024.
- weatherIDW.csv: meteorological data obtained from [`meteostat`](https://dev.meteostat.net/).
- dictionary_areas_ACTUAL_df.json: the original dataset contains the name of each area. For practical purposes we enumerate them from 1 to $N$. This is the dictionary of the mapping.

## Notebook description 
The notebook, `distance_analysis_v6.ipynb`, includes the scripts to perform the pre-processing and for obtaining the previous `*.csv` files, if you decide to double-check. However, it could be computational expensive and for that reason it is recommended to use the `*.csv` files directly. The scripts to read the files are also included. <span style="color:#ff6b6b">But in case of pulling the repository is needed to change the direction (to be updated).</span>
