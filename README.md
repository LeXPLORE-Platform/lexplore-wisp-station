# LéXPLORE WISP Station

Eawag maintains a [WISP Station](https://www.waterinsight.nl/info/wispstation-fixed-position-autonomous-water-quality-spectrometer) on the floating scientific platform on Lake Geneva.
Based on the colour of the surface water, it determines the most important bio-physical water quality parameters, such as chlorophyll, cyanobacteria pigment, suspended matter, presence of scums and transparency.

Data from the station is automatically sent to [Water Insight](https://www.waterinsight.nl/) where it is available to download from
their WISPcloud service. A tutorial for how to access data from this service is provided `notebooks/WISPcloud API tutorial.ipynb`.

This repository collects the data from the WISPcloud and processes it to NetCDF files compatible, 
with display on the [Datalakes](https://www.datalakes-eawag.ch/) data portal.

## Sensors

The WISP station records the spectral signature (350-900nm in 1nm steps) of the surface water at 15 minute intervals during daylight hours.

## Calibration

Calibration of the optical sensors is funded by SCNAT

![SCNAT Logo](https://datalakes-eawag.s3.eu-central-1.amazonaws.com/images/scnat.png)

## Installation

You need to have git and git-lfs installed in order to successfully clone the repository.

- Clone the repository to your local machine using the command: 

 `git clone --depth 1 https://github.com/LeXPLORE-Platform/lexplore-wisp-station.git`
 
- Use conda and install the requirements with:

`conda env create -f environment.yml`

## Usage

### Credentials

In order to download live data `creds_example.json` should be renamed to `creds.json` and completed.

### Operation

To run the pipeline: `python scripts/main.py`

The python script `scripts/main.py` defines the different processing steps while the python script `scripts/meteostation.py` contains the python class meteostation with all the corresponding class methods to process the data. To add a new processing or visualization step, a new class method can be created in the `meteostation.py` file and the step can be added in `main.py` file. Both above mentioned python scripts are independent of the local file system.

### Arguments

Run `scripts/main.py -h` for details on the input arguments available


## Data

The data can be found in the folder `data`. `Spectral` refers to raw spectral data from the WISP station and `Water Quality` refers to water quality parameters derived from the spectra (calculated by Water Insights).

The data is structured as follows:

### Data Structure

- **Level 0**: Raw data collected from the WISPcloud API.

- **Level 1**: Raw data stored to NetCDF file where attributes (such as sensors used, units, description of data, etc.) are added to the data. 
Column with quality flags are added to the data. Quality flag "1" indicates that the data point didn't pass the 
quality checks and further investigation is needed, quality flag "0" indicates that no further investigation is needed.

## Quality assurance

Quality checks include checking values are in a realistic range.
