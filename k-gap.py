#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" k-gap calculation script

@author: sanjanamendu
"""

from geopy.distance import GeodesicDistance
from datetime import datetime
import itertools as it
from tqdm import tqdm
import pandas as pd

max_d, max_t = 100, 60

# %% Helper functions
def sample_stretch_effort(s_i, s_j):
    return 0.5 * spatial_stretch(s_i, s_j) + 0.5 * temporal_stretch(s_i, s_j)
    
# Distance between two points
def spatial_stretch(s_i, s_j):
    dist = GeodesicDistance((s_i.lat,s_i.lon),(s_j.lat,s_j.lon)).km * 1000
    return dist/max_d if (dist <= max_d) else 1
    
# Overlap between two time intervals
def temporal_stretch(s_i, s_j):
    overlap =  (min(s_i.end,s_j.end)-max(s_i.start,s_j.start)).total_seconds()
    return overlap/(max_t * 60) if (overlap >= 0) and (overlap <= max_t * 60) else 1

# K-gap between two fingerprints
def k_gap(f1,f2):
    sse = [min([sample_stretch_effort(s_i, s_j) for j, s_j in f2.iterrows()]) for i, s_i in f1.iterrows()]
    return sum(sse) / f1.shape[0]

def get_trace(df,sid):
    return df[df['SubjectID'] == sid].copy().reset_index(drop=True)

# %% Format data
parameters = [[60,100,3]] # [1,0.1,6], [10,1,5], [30,10,4], 

for temporal_threshold, spatial_threshold, max_dd in parameters:

    dbscan_df = pd.read_csv("output/cluster/" + str(temporal_threshold) + "_" + str(spatial_threshold) + ".csv") \
                  .round({'lat': max_dd, 'lon': max_dd, 'DBSCAN_Lat': max_dd, 'DBSCAN_Lon': max_dd})
    dbscan_df['start'] = dbscan_df['start_time'].apply(lambda x: datetime.fromtimestamp(x))
    dbscan_df['end'] = dbscan_df['end_time'].apply(lambda x: datetime.fromtimestamp(x))
    dbscan_df = dbscan_df.rename(columns={'lat':'latitude', 'lon':'longitude', 'DBSCAN_Lat':'lat', 'DBSCAN_Lon':'lon'})

# %% The main loop
    participants = dbscan_df['SubjectID'].unique().tolist()[:10]
    pairs = [(a,b) for (a,b) in it.combinations(participants, 2)]
    fingerprints = [(get_trace(dbscan_df,a),get_trace(dbscan_df,b)) for (a,b) in pairs]
    gaps = [k_gap(f_a,f_b) if f_a.shape[0] < f_b.shape[0] else k_gap(f_b,f_a) for (f_a,f_b) in tqdm(fingerprints)]
    
    df = pd.DataFrame(index=participants[:10],columns=participants[:10])
    for i in range(len(pairs)):
        (a,b) = pairs[i]
        df.loc[a][b] = gaps[i]
        df.loc[b][a] = gaps[i]
    df.to_csv("output/k-gap/" + str(temporal_threshold) + "_" + str(spatial_threshold) + ".csv")
