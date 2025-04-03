# -*- coding: utf-8 -*-
import netCDF4
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from os import path, remove

def water_quality_download(date_string, folder, user, password):
    url = "https://wispcloud.waterinsight.nl/api/query?SERVICE=Data&VERSION=1.0&REQUEST=GetData&INSTRUMENT=WISPstation017&TIME=" + date_string + "T00:00," + date_string + "T23:59"
    filename = "Lexplore_Water_Quality_" + date_string + ".txt"
    filepath = path.join(folder, filename)
    if path.exists(filepath):
        remove(filepath)
    response = requests.get(url, allow_redirects=True, auth=(user, password))
    open(filepath, 'wb').write(response.content)
    return filepath


def spectral_download(date_string, folder, user, password):
    url = "https://wispcloud.waterinsight.nl/api/query?SERVICE=Data&VERSION=1.0&REQUEST=GetData&INSTRUMENT=WISPstation017&TIME="+date_string+"T00:00,"+date_string+"T23:59&INCLUDE=measurement.id,measurement.date,instrument.name,ed.irradiance,ld.radiance,lu.radiance,level2.reflectance,ld.selected,lu.selected,ed.selected"
    filename = "Lexplore_Spectral_" + date_string + ".txt"
    filepath = path.join(folder, filename)
    if path.exists(filepath):
        remove(filepath)
    response = requests.get(url, allow_redirects=True, auth=(user, password))
    open(filepath, 'wb').write(response.content)
    return filepath
