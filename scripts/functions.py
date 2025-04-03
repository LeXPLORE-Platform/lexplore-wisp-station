# -*- coding: utf-8 -*-
import time
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

    max_retries = 5
    attempt = 0

    while attempt < max_retries:
        response = requests.get(url, allow_redirects=True, auth=(user, password))

        if response.status_code == 200:
            open(filepath, 'wb').write(response.content)
            return filepath
        else:
            print(f"Attempt {attempt + 1}: Failed with status {response.status_code}. Retrying in 10 seconds...")
            time.sleep(10)
            attempt += 1
    else:
        print("Max retries reached. Request failed.")
    return False


def spectral_download(date_string, folder, user, password):
    url = "https://wispcloud.waterinsight.nl/api/query?SERVICE=Data&VERSION=1.0&REQUEST=GetData&INSTRUMENT=WISPstation017&TIME="+date_string+"T00:00,"+date_string+"T23:59&INCLUDE=measurement.id,measurement.date,instrument.name,ed.irradiance,ld.radiance,lu.radiance,level2.reflectance,ld.selected,lu.selected,ed.selected"
    filename = "Lexplore_Spectral_" + date_string + ".txt"
    filepath = path.join(folder, filename)
    if path.exists(filepath):
        remove(filepath)

    max_retries = 5
    attempt = 0

    while attempt < max_retries:
        response = requests.get(url, allow_redirects=True, auth=(user, password))

        if response.status_code == 200:
            open(filepath, 'wb').write(response.content)
            return filepath
        else:
            print(f"Attempt {attempt + 1}: Failed with status {response.status_code}. Retrying in 10 seconds...")
            time.sleep(10)
            attempt += 1
    else:
        print("Max retries reached. Request failed.")
    return False
