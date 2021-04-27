#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 21:28:20 2021

  Read in the raw GPS data from a csv file and format as a list of 
  chronologically ordered pandas DataFrames for each participant

@author: sanjanamendu
"""

from tqdm import tqdm
import pandas as pd
import glob
import os

places = []

for f in tqdm(glob.glob("../dataset/sensing/gps/gps_*.csv")):
    df = pd.read_csv(f,index_col=False)
    df["Participant"] = os.path.basename(f).split("_")[1].split(".")[0]
    df = df.sort_values(by="time", ascending=True).reset_index(drop=True)
    df = df.rename(columns={"Participant": "SubjectID", "latitude": "lat", "longitude": "lon"})
    df = df[['SubjectID', 'lat', 'lon', 'time']]
    places.append(df)

pd.concat(places).to_csv("output/gps-merged.csv",index=False)