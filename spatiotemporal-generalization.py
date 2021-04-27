# -*- coding: utf-8 -*-
"""Spatiotemporal Generalization Script

@author: sanjanamendu
"""

from tqdm import tqdm
import pandas as pd

parameters = [[1,0.1,6], [10,1,5], [30,10,4], [60,100,3]]

for temporal_threshold, spatial_threshold, max_dd in parameters:
    
#%% --------------------------- SPATIO-TEMPORAL --------------------------------
# Use create_place_clusters function in stc.py file to
# apply spatio-temporal clustering algorithm to each participant's data

    from stc import create_place_clusters
    
    df = pd.read_csv("output/gps-merged.csv")
    places = [df_i.reset_index(drop=True) for i, df_i in df.groupby('SubjectID')]
    
    final_clusters = [create_place_clusters(i, spatial_threshold, temporal_threshold * 60) for i in tqdm(places)]
    stc_df = pd.concat(final_clusters, 
                       keys=df.SubjectID.unique(), \
                       sort=False).reset_index(level=0) \
                                  .rename(columns={'level_0': 'SubjectID'}) \
                                  .reset_index(drop=True)
    
    stc_df['start_time'] = stc_df.start_time.astype(int)
    stc_df['time_durations'] = stc_df.time_durations.astype(int)
    stc_df["end_time"] = stc_df.start_time + stc_df.time_durations

#%%  --------------------------- DBSCAN -----------------------------------------
# Use perform_DBSCAN function in dbscan.py file to consolidate spatially 
# dense spatio-temporal clusters from the previous clustering step

    from dbscan import perform_DBSCAN
    
    clusters = []
    for i, df_sub in tqdm(stc_df.groupby('SubjectID')):
        coords = df_sub[['lat', 'lon']].copy().values
        cluster_labels, centermost_points = perform_DBSCAN(coords, eepsilon=spatial_threshold / 1000)
        
        df_sub["DBScan_labels"] = cluster_labels
        df_sub['DBScan_loc'] = df_sub.apply(lambda row: centermost_points[row["DBScan_labels"]], axis=1).astype(str)
    
        df_sub = pd.concat([df_sub,df_sub['DBScan_loc'].str.strip('()')
                                                       .str.split(', ', expand=True)
                                                       .rename(columns={0: 'DBSCAN_Lat', 1: 'DBSCAN_Lon'})], axis=1)
    
        clusters.append(df_sub)
        
    dbscan_df = pd.concat(clusters)
    
    dbscan_df = dbscan_df.round({'lat': max_dd, 'lon': max_dd, 'DBSCAN_Lat': max_dd, 'DBSCAN_Lon': max_dd})
    dbscan_df['start_time'] = dbscan_df['start_time'].apply(lambda x: x // (temporal_threshold) * (temporal_threshold))
    dbscan_df['end_time'] = dbscan_df['end_time'].apply(lambda x: x // (temporal_threshold) * (temporal_threshold))
    
    dbscan_df.to_csv("output/cluster/" + str(temporal_threshold) + "_" + str(spatial_threshold) + ".csv", index=False)