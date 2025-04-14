# -*- coding: utf-8 -*-
import netCDF4
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from os import path, remove

def is_number(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return True

class WaterQuality(object):
    def __init__(self):
        self.att = {
            "institution": "EAWAG",
            "source": "Lexplore Water Quality Data",
            "history": "See history on Renku",
            "conventions": "CF 1.7",
            "comment": "Water quality parameters derived from the spectral recorder on the Lexplore platform in Lake Geneva",
            "title": "Lexplore Water Quality Data"
        }

        self.dim_dict = {
            'time': {'dim_name': 'time', 'dim_size': None},
        }

        self.dim_var_dict = {
            'time': {'var_name': 'time', 'dim': ('time',), 'unit': 'seconds since 1970-01-01 00:00:00',
                     'longname': 'time'},
        }

        self.var_dict = {
            'tsm': {'var_name': 'tsm', 'dim': ('time',), 'unit': 'g m-3', 'longname': 'Total Suspended Matter'},
            'chla': {'var_name': 'chla', 'dim': ('time',), 'unit': 'mg m-3', 'longname': 'Chlorophyll A'},
            'kd': {'var_name': 'kd', 'dim': ('time',), 'unit': 'm-1',
                   'longname': 'Diffuse Attenuation Coefficient of Downwelling Irradiance'},
        }

        self.data = {}

    def read_data(self, input_file_path):
        with open(input_file_path) as f:
            first_line = f.readline()
        header_size = int(''.join(filter(str.isdigit, first_line))) + 1
        df = pd.read_csv(input_file_path, header=header_size, delimiter="	")
        df.columns = ['station', 'time', 'id', 'tsm', 'chla', 'kd']
        df.replace('None', np.nan, inplace=True)

        # Check if file is empty
        if len(df) == 1 and (str(df.iloc[0]['time']) in ['None', 'nan']):
            return False

        self.data['time'] = np.array(pd.to_datetime(df['time']).astype(int) / 10 ** 9)
        for variable in self.var_dict:
            self.data[variable] = np.array(df[variable])
        return True

    def export_to_netcdf(self, output_directory, level):
        dt = datetime.utcfromtimestamp(self.data["time"][0]).strftime('%Y%m%d_%H%M%S')
        filename = level + "_Lexplore_WaterQuality_" + dt + ".nc"
        filepath = path.join(output_directory, filename)
        if path.exists(filepath):
            remove(filepath)

        # Create new NetCDF file
        ncfile = netCDF4.Dataset(filepath, mode='w', format='NETCDF4')

        # Add global attributes
        for key in self.att:
            setattr(ncfile, key, self.att[key])

        # Create Dimensions
        for key, values in self.dim_dict.items():
            ncfile.createDimension(values['dim_name'], values['dim_size'])

        # Create Dimensions Variables
        for key, values in self.dim_var_dict.items():
            var = ncfile.createVariable(values["var_name"], np.float64, values["dim"])
            var.units = values["unit"]
            var.long_name = values["longname"]
            var[:] = self.data[key]

        # Create Variables
        for key, values in self.var_dict.items():
            var = ncfile.createVariable(values["var_name"], np.float64, values["dim"])
            var.units = values["unit"]
            var.long_name = values["longname"]
            var[:] = list(self.data[key])

        # Close NetCDF file
        ncfile.close()

        return filepath

    def quality_assurance(self):
        variables = self.var_dict.copy().items()
        for key, values in variables:
            if key not in ["ld", "lu", "ed"]:
                name = key + "_qual"
                self.var_dict[name] = {'var_name': name, 'dim': ('time',),
                                        'unit': '0 = nothing to report, 1 = more investigation',
                                        'longname': name, }
                qa_data = []
                for dp in self.data[key]:
                    qa = 0
                    if not is_number(dp):
                        qa = 1
                    if "min" in values and float(dp) < float(values["min"]):
                        qa = 1
                    if "max" in values and float(dp) > float(values["max"]):
                        qa = 1
                    qa_data.append(qa)
                self.data[name] = qa_data


class Spectral(object):
    def __init__(self):
        self.att = {
            "institution": "EAWAG",
            "source": "Lexplore Spectral Data",
            "history": "See history on Renku",
            "conventions": "CF 1.7",
            "comment": "Data from spectral recorder on  Lexplore",
            "title": "Lexplore Spectral Data"
        }

        self.dim_dict = {
            'time': {'dim_name': 'time', 'dim_size': None},
            'wavelength': {'dim_name': 'wavelength', 'dim_size': None}
        }

        self.dim_var_dict = {
            'time': {'var_name': 'time', 'dim': ('time',), 'unit': 'seconds since 1970-01-01 00:00:00',
                     'longname': 'time'},
            'wavelength': {'var_name': 'wavelength', 'dim': ('wavelength',), 'unit': 'nm', 'longname': 'wavelength'}
        }

        self.var_dict = {
            'downirr': {'var_name': 'downirr', 'dim': ('wavelength', 'time',), 'unit': 'W/(m2*nm)',
                        'longname': 'Downwelling irradiance'},
            'downrad': {'var_name': 'downrad', 'dim': ('wavelength', 'time',), 'unit': 'W/(m2*nm*sr)',
                        'longname': 'Downwelling radiance'},
            'uprad': {'var_name': 'uprad', 'dim': ('wavelength', 'time',), 'unit': 'W/(m2*nm*sr)',
                      'longname': 'Upwelling radiance'},
            'rsr': {'var_name': 'rsr', 'dim': ('wavelength', 'time',), 'unit': '1/sr',
                    'longname': 'Remote sensing reflectance'},
            'ld': {'var_name': 'ld', 'dim': ('time',), 'unit': 'LdS = 0, LdP = 1', 'longname': 'Ld selected sensor'},
            'lu': {'var_name': 'lu', 'dim': ('time',), 'unit': 'LuS = 0, LuP = 1', 'longname': 'Lu selected sensor'},
            'ed': {'var_name': 'ed', 'dim': ('time',), 'unit': 'EdF = 0, EdA = 1', 'longname': 'Ed selected sensor'},
        }

        self.data = {}

    def read_data(self, input_file_path):
        with open(input_file_path) as f:
            first_line = f.readline()
        header_size = int(''.join(filter(str.isdigit, first_line))) + 1
        df = pd.read_csv(input_file_path, header=header_size, delimiter="	")
        df.columns = ['id', 'time', 'station', 'downirr', 'downrad', 'uprad', 'rsr', 'ld', 'lu', 'ed']
        df.replace('None', np.nan, inplace=True)
        # Check if file is empty
        if len(df) == 1 and (str(df.iloc[0]['time']) in ['None', 'nan']):
            print("File {} contains no data".format(path.basename(input_file_path)))
            return False

        # Process sensor information
        df["ld"] = df["ld"].replace("LdS", 0).replace("LdP", 1)
        df["lu"] = df["lu"].replace("LuS", 0).replace("LuP", 1)
        df["ed"] = df["ed"].replace("EdF", 0).replace("EdA", 1)

        self.data['wavelength'] = np.array(range(350, 901, 1))
        self.data['time'] = np.array(pd.to_datetime(df['time']).astype(int) / 10 ** 9)

        for variable in self.var_dict:
            if len(self.var_dict[variable]["dim"]) == 2:
                y = []
                for idx in range(len(df)):
                    y.append(eval(list(df[variable])[idx]))
                self.data[variable] = np.swapaxes(np.array(y), 0, 1)
            else:
                self.data[variable] = np.array(df[variable])
        return True

    def export_to_netcdf(self, output_directory, level):
        dt = datetime.utcfromtimestamp(self.data["time"][0]).strftime('%Y%m%d_%H%M%S')
        filename = level + "_Lexplore_Sprectral_" + dt + ".nc"
        filepath = path.join(output_directory, filename)
        if path.exists(filepath):
            remove(filepath)

        # Create new NetCDF file
        ncfile = netCDF4.Dataset(filepath, mode='w', format='NETCDF4')

        # Add global attributes
        for key in self.att:
            setattr(ncfile, key, self.att[key])

        # Create Dimensions
        for key, values in self.dim_dict.items():
            ncfile.createDimension(values['dim_name'], values['dim_size'])

        # Create Dimensions Variables
        for key, values in self.dim_var_dict.items():
            var = ncfile.createVariable(values["var_name"], np.float64, values["dim"])
            var.units = values["unit"]
            var.long_name = values["longname"]
            var[:] = self.data[key]

        # Create Variables
        for key, values in self.var_dict.items():
            var = ncfile.createVariable(values["var_name"], np.float64, values["dim"])
            var.units = values["unit"]
            var.long_name = values["longname"]
            if len(values["dim"]) == 1:
                var[:] = self.data[key]
            else:
                var[:, :] = self.data[key]

        # Close NetCDF file
        ncfile.close()

        return filepath

    def quality_assurance(self):
        variables = self.var_dict.copy().items()
        for key, values in variables:
            if key not in ["ld", "lu", "ed"]:
                name = key + "_qual"
                dims = self.var_dict[key]["dim"]
                self.var_dict[name] = {'var_name': name, 'dim': dims,
                                        'unit': '0 = nothing to report, 1 = more investigation',
                                        'longname': name, }

                qa_data = []
                if len(dims) == 2:
                    for i in range(len(self.data[key])):
                        qa_data_inner = []
                        for j in range(len(self.data[key][i])):
                            qa = 0
                            if not is_number(self.data[key][i][j]):
                                qa = 1
                            if "min" in values and float(self.data[key][i][j]) < float(values["min"]):
                                qa = 1
                            if "max" in values and float(self.data[key][i][j]) > float(values["max"]):
                                qa = 1
                            qa_data_inner.append(qa)
                        qa_data.append(qa_data_inner)
                else:
                    for dp in self.data[key]:
                        qa = 0
                        if not is_number(dp):
                            qa = 1
                        if "min" in values and float(dp) < float(values["min"]):
                            qa = 1
                        if "max" in values and float(dp) > float(values["max"]):
                            qa = 1
                        qa_data.append(qa)
                self.data[name] = qa_data
