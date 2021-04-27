# -*- coding: utf-8 -*-
"""Density-based Spatial Clustering of Applications with Noise (DBSCAN)

This script contains all functions required to execute the DBSCAN clustering 
algorithm. This code is taken from 
https://geoffboeing.com/2014/08/clustering-to-reduce-spatial-data-set-size/

This script requires that `numpy`, `pandas`, `sklearn`, `geopy`, and `shapely`
be installed within the Python environment you are running this script in.

This file can be imported as a module and contains the following functions:

    * get_centroid - Get the latitude/longitude tuple corresponding to the center of the given cluster
    * perform_DBSCAN - Executes DBSCAN clustering algorithm

"""

import numpy as np
import pandas as pd

from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint

def get_centroid(cluster):
    """ Get the long/long coordinate corresponding to the center of the given cluster

    Parameters
    ----------
    cluster : list of tuples
        list of lat/long coordinates belonging to a given cluster

    Returns
    -------
    tuple
        lat/long coordinates for the centroid of `cluster`
    """
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(
        cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def perform_DBSCAN(coords, eepsilon=0.04):
    """ Executes DBSCAN clustering algorithm

    Parameters
    ----------
    coords : 2D numpy array
        list of lat/long coordinates
    eepsilon : float
        maximum distance (in kilometers) that points can be from each other to be considered a cluster
        default value is 0.04 (i.e. 0.04km or 40m)

    Returns
    -------
    cluster_labels: list of int
        list of cluster assignments for each lat/long coordinate in `coords`
    centermost_points: list of tuples
        list of DBSCAN cluster centroids
    """
    kms_per_radian = 6371.0088
    epsilon = eepsilon / kms_per_radian
    db = DBSCAN(
        eps=epsilon,
        min_samples=1,
        algorithm='ball_tree',
        metric='haversine').fit(
        np.radians(coords))
    cluster_labels = db.labels_
    
    num_clusters = len(set(cluster_labels)) # number of clusters after performing DBSCAN
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    centermost_points = clusters.map(get_centroid)
    return cluster_labels, centermost_points
