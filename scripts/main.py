# -*- coding: utf-8 -*-
import os
import sys
import yaml
import json
import time
import argparse
import requests
import configparser
from datetime import datetime, date, timedelta
from instruments import WaterQuality, Spectral
from general.functions import logger
from functions import spectral_download, water_quality_download

def main(server=False, logs=False):
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if logs:
        log = logger(os.path.join(repo, "logs/wisp"))
    else:
        log = logger()
    log.initialise("Processing LéXPLORE WISP data")
    directories = {f: os.path.join(repo, "data", f) for f in ["Level0", "Level1"]}
    for directory in directories:
        os.makedirs(directories[directory], exist_ok=True)
        for f in ["Spectral", "WaterQuality"]:
            os.makedirs(os.path.join(directories[directory], f), exist_ok=True)

    l0_spectral = os.path.join(directories["Level0"], "Spectral")
    l0_wq = os.path.join(directories["Level0"], "WaterQuality")

    log.begin_stage("Collecting inputs")
    if server:
        log.info("Processing files from WISP server")
        if not os.path.exists(os.path.join(repo, "creds.json")):
            raise ValueError("Credential file required to retrieve live data from the fstp server.")
        with open(os.path.join(repo, "creds.json"), 'r') as f:
            creds = json.load(f)
        params = configparser.ConfigParser()
        params_file = os.path.join(repo, "lastupdated.ini")
        if os.path.exists(params_file):
            params.read(os.path.join(repo, "lastupdated.ini"))
        else:
            params["Updated"] = {"datetime": (date.today() - timedelta(days=1)).strftime(r"%Y-%m-%dT%H:%M:%SZ")}
        process_date = datetime.strptime(params['Updated']['datetime'], r"%Y-%m-%dT%H:%M:%SZ")
        end_date = datetime.combine(date.today(), datetime.max.time())
        files = []
        while process_date < end_date:
            date_string = process_date.strftime(r"%Y-%m-%d")
            log.info("Downloading {}".format(date_string), indent=1)
            file = spectral_download(date_string, l0_spectral, creds["user"], creds["password"])
            if file:
                files.append(file)
            file = water_quality_download(date_string, l0_wq, creds["user"], creds["password"])
            if file:
                files.append(file)
            process_date = process_date + timedelta(days=1)
        params['Updated']['datetime'] = date.today().strftime(r"%Y-%m-%dT%H:%M:%SZ")
        with open(os.path.join(repo, "lastupdated.ini"), "w") as f:
            params.write(f)
    else:
        files = [os.path.join(l0_spectral, f) for f in os.listdir(l0_spectral)] + [os.path.join(l0_wq, f) for f in os.listdir(l0_wq)]
        files.sort()
        log.info("Reprocessing complete dataset from {}".format(directories["Level0"]))
    log.end_stage()

    log.begin_stage("Processing data to L1")
    edited_files = []
    for file in files:
        try:
            if "/Spectral/" in file:
                spectral = Spectral()
                if spectral.read_data(file):
                    spectral.quality_assurance()
                    edited_files.append(spectral.export_to_netcdf(os.path.join(directories["Level1"], "Spectral"), "L1"))
            else:
                water_quality = WaterQuality()
                if water_quality.read_data(file):
                    water_quality.quality_assurance()
                    water_quality.export_to_netcdf(os.path.join(directories["Level1"], "WaterQuality"), "L1")
        except:
            log.info("Failed for {}".format(file), indent=1)

    log.end_stage()

    return edited_files + files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', help="Collect and process new files from FTP server", action='store_true')
    parser.add_argument('--logs', '-l', help="Write logs to file", action='store_true')
    args = vars(parser.parse_args())
    main(server=args["server"], logs=args["logs"])