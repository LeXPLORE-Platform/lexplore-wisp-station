# LéXPLORE WISP Station

Eawag maintains a [WISP Station](https://www.waterinsight.nl/info/wispstation-fixed-position-autonomous-water-quality-spectrometer) on the floating scientific platform on Lake Geneva.
Based on the colour of the surface water, it determines the most important bio-physical water quality parameters, such as chlorophyll, cyanobacteria pigment, suspended matter, presence of scums and transparency.

Data from the station is automatically sent to [Water Insight](https://www.waterinsight.nl/) where it is available to download from
their WISPcloud service. A tutorial for how to access data from this service is provided `notebooks/WISPcloud API tutorial.ipynb`.

This repository collects the data from the WISPcloud and processes it to NetCDF files compatible, 
with display on the [Datalakes](https://www.datalakes-eawag.ch/) data portal.

## Sensors

The WISP station records the spectral signature (350-900nm in 1nm steps) of the surface water at 15 minute intervals during daylight hours.

## Installation

You need to have git and git-lfs installed in order to successfully clone the repository.

- Clone the repository to your local machine using the command: 

 `git clone --depth 1 https://renkulab.io/gitlab/lexplore/wisp-station.git`
 
 Note that the repository will be copied to your current working directory.

- Use Python 3 and install the requirements with:

 `pip install -r requirements.txt`

 The python version can be checked by running the command `python --version`. In case python is not installed or only an older version of it, it is recommend to install python through the anaconda distribution which can be downloaded [here](https://www.anaconda.com/products/individual). 

## Data

The data can be found in the folder `data`. `Spectral` refers to raw spectral data from the WISP station and `Water Quality` refers to water quality parameters derived from the spectra (calculated by Water Insights).

The data is structured as follows:

### Data Structure

- **Level 0**: Raw data collected from the WISPcloud API.

- **Level 1A**: Raw data stored to NetCDF file where attributes (such as sensors used, units, description of data, etc.) are added to the data. 

- **Level 1B**: Column with quality flags are added to the Level 1A data. Quality flag "1" indicates that the data point didn't pass the 
quality checks and further investigation is needed, quality flag "0" indicates that no further investigation is needed.

## Quality assurance

Quality checks include checking values are in a realistic range.
