# -*- coding: utf-8 -*-
"""Spatio-temporal Clustering Algorithm

This script contains all functions required to execute the spatio-temporal
clustering algorithm described in the following paper:

    Boukhechba, M., Chow, P., Fua, K., Teachman, B. A., & Barnes, L. E. (2018).
    Predicting social anxiety from global positioning system traces of college
    students: feasibility study. JMIR mental health, 5(3), e10101.

This script requires that `pandas` and `geopy` be installed within the Python
environment you are running this script in.

This file can be imported as a module and contains the following functions:

    * dist_point - Finds distance between any two points
    * get_centroid - Get the latitude/longitude tuple corresponding to the center of the given cluster
    * get_centroid_lat - Get the latitude of the center of the given cluster
    * get_centroid_long - Get the longitude of the center of the given cluster
    * dist_cluster_new_loc - Finds the distance between the cluster and the loc, using the centroid
    * time_duration - Returns the total time spent at a given cluster
    * create_place_clusters - Executes spatio-temporal clustering algorithm described by Boukhechba et al.

"""

import pandas as pd
import geopy.distance


def dist_point(loc1, loc2):
    """ Finds distance between any two points

    Parameters
    ----------
    loc1 : tuple
        latitude/longitude values for first point
    loc2 : tuple
        latitude/longitude values for second point

    Returns
    -------
    float
        geodesic distance between two points (i.e. `loc1` and `loc2`)
    """
    return(geopy.distance.geodesic(loc1, loc2).km) * 1000


def get_centroid(cluster_loc):
    """ Get the latitude/longitude tuple corresponding to the center of the given cluster

    Parameters
    ----------
    cluster_loc : list of tuples
        list of lat/long coordinates belonging to a given cluster

    Returns
    -------
    tuple
        lat/long coordinates for the centroid of `cluster_loc`
    """
    lat, long = [], []
    for l in cluster_loc:
        lat.append(l['loc'][0])
        long.append(l['loc'][1])
    return sum(lat) / len(lat), sum(long) / len(long)


def get_centroid_lat(cluster_loc):
    """ Get the latitude of the center of the given cluster

    Parameters
    ----------
    cluster_loc : list of tuples
        list of lat/long coordinates belonging to a given cluster

    Returns
    -------
    float
        latitude corresponding to the centroid of `cluster_loc`
    """
    lat = [l['loc'][0] for l in cluster_loc]
    return sum(lat) / len(lat)


def get_centroid_long(cluster_loc):
    """ Get the longitude of the center of the given cluster

    Parameters
    ----------
    cluster_loc : list of tuples
        list of lat/long coordinates belonging to a given cluster

    Returns
    -------
    float
        longitude corresponding to the centroid of `cluster_loc`
    """
    long = [l['loc'][1] for l in cluster_loc]
    return sum(long) / len(long)


def dist_cluster_new_loc(cluster, new_loc):
    """ Finds the distance between the centroid of a given cluster and a point

    Parameters
    ----------
    cluster : list of tuples
        list of lat/long coordinates belonging to a given cluster
    new_loc : tuple
        lat/long coordinates of point

    Returns
    -------
    float
        distance between the centroid of `cluster` and `new_loc`
    """
    return (geopy.distance.geodesic(get_centroid(cluster), new_loc['loc']).km) * 1000


def time_duration(cluster):
    """ Returns the total time spent at a given cluster

    Parameters
    ----------
    cluster : list of tuples
        list of lat/long coordinates belonging to a given cluster

    Returns
    -------
    float
        time (in seconds) spent at `cluster`
    """
    return cluster[len(cluster) - 1]['time'] - cluster[0]['time']


def create_place_clusters(data_places, distance_threshold, time_threshold):
    """ Executes spatio-temporal clustering algorithm described by Boukhechba
        et al. (see paper for pseudocode implementation)

    Parameters
    ----------
    data_places : pandas.DataFrame
        pandas DataFrame containing raw GPS traces (i.e. lat, lon, and time columns)
    distance_threshold : int
        maximum radius (in meters) of any cluster
    time_threshold : int
        maximum time (in seconds) between sequential points in any cluster

    Returns
    -------
    pandas.DataFrame
        pandas DataFrame containing results of spatio-temporal clustering algorithm
    """

    # list of the clusters with cluster's startpoint, time duration and the time spent.
    final_clusters = []

    # defining the first loc
    first_loc = data_places.iloc[0]
    first_loc_entry = {
        'loc': (
            first_loc['lat'],
            first_loc['lon']),
        'time': first_loc['time']}

    cur_cluster = [first_loc_entry]  # we start with the first loc
    ploc = None  # ploc (i.e. placeholder location) is taken to be just one variable, not the list

    for index, row in data_places.drop(
            0).iterrows():  # start itertating from second location in dataframe

        new_loc = {'loc': (row['lat'], row['lon']), 'time': row['time']}

        if(dist_cluster_new_loc(cur_cluster, new_loc) < distance_threshold):
            # Distance from cur_cluster to new_loc <  distance_threshold. Adding new_loc to cur_cluster
            cur_cluster.append(new_loc)
            ploc = None

        else:
            if ploc is not None:
                # 2nd out-of-cluster point found (ploc is not None)

                if(time_duration(cur_cluster) > time_threshold):
                    # Time duration of current visit (cur_cluster) > time_threshold. Adding cur_cluster to final clusters
                    final_clusters.append({'lat': get_centroid_lat(cur_cluster), 'lon': get_centroid_long(
                        cur_cluster), 'time_durations': time_duration(cur_cluster), 'start_time': cur_cluster[0]['time']})

                # Overwriting cur_cluster to document new visit, and adding
                # ploc as the first point
                cur_cluster = []
                cur_cluster.append(ploc)

                if(dist_cluster_new_loc(cur_cluster, new_loc) < distance_threshold):
                    # Distance from cur_cluster to new_loc < distance_threshold. Adding new_loc to cur_cluster (along with ploc)
                    cur_cluster.append(new_loc)
                    ploc = None

                else:
                    # Distance from cur_cluster to new_loc > distance_threshold. Setting new_loc as new ploc
                    ploc = new_loc

            else:
                # 1st out-of-cluster point found. Setting new_loc to as new ploc
                ploc = new_loc

    return pd.DataFrame(final_clusters)
