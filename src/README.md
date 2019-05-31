# Crash model pipeline

This directory contains the code for taking the data from the csv crash files, standardizing the crash data, generating the feature set, training a model to predict risk on segments, and visualizing the results.

## Module dependencies
If using conda, you can get all the depencies using the [environment_linux.yml](https://github.com/Data4Democracy/crash-model/blob/master/environment_linux.yml), [environment_mac.yml](https://github.com/Data4Democracy/crash-model/blob/master/environment_mac.yml), or [environment_pc.yml](https://github.com/Data4Democracy/crash-model/blob/master/environment_pc.yml) files.
Python modules: Use requirements\_spatial.txt

rtree additionally requires download and installation of [libspatialindex](http://libspatialindex.github.io/)
(For Anaconda install, can use [conda-forge](https://anaconda.org/conda-forge/libspatialindex))

## Useful Tools

Although it's not necessary, QGIS (http://www.qgis.org/en/site/forusers/download.html) might be helpful to visualize shape files and easily see their attributes

## Code conventions

## Testing

We use Travis continuous integration to ensure that our test suite passes before branches can be merged into master.  To run the tests locally, run `py.test` in the src/ directory.

## Overview

We use open street map to generate basic information about a city.  Then we find intersections and segments in between intersections.  We take one or more csv files of crash data and map crashes to the intersection or non-intersection segments on our map.  And we have the ability to add a number of other data sources to generate features beyond those from open street map.  Most of the additional features are currently Boston-specific.
These features include
- Concerns submitted to the city of Boston's vision zero platform http://app01.cityofboston.gov/VZSafety/.  Concerns are not Boston-specific, but not very many cities gather these type of concerns.  Some other cities have other sources of concern data.  We use See Click Fix data (https://seeclickfix.com/) as our concern data for Cambridge, MA.
- Any other point-based feature (in a csv file with a latitude and longitude).
- Automated traffic counts in some locations
- Turning movement counts in some locations

We also can map city-specific maps (and features associated with their roads) to the base open street map.

## Running the pipeline: data generation through visualization

This section walks you through how to generate and visualize data for any of our demo cities (Boston MA, Cambridge MA or Washigton D.C), or for any city that you have suitable data for (at a minimum crashes, ideally concerns as well).

The demo city data is stored as *data-latest.zip* using data-world. Contact one of the project leads if you don't yet have access.

### Visualization
- If you want to visualize the data, you'll need to create a mapbox account (https://www.mapbox.com/)

### Initializing a city
- If you're running on a new city (that does not have a configuration file in src/data/config), you will need to initialize it first to create directories and generate a config.  In the src directory, run `python initialize_city.py -city <city name> -f <folder name> -crash <crash file> --supplemental <supplemental file1>,<supplemental file2>`. You should give the full path to the crash file and any supplemental files, and they will be copied into the city's data directory as part of initialization. Concern files are given as supplemental files, as are any other point-based features.
    - City name is the full name of the city, e.g. "Cambridge, MA, USA".
    - Folder name is what you'd like the city's data directory to be named, e.g. "cambridge".
    - The latitude and longitude will be auto-populated by the initialize_city script, but you can modify this
    - The time zone will be auto-populated as your current time zone, but you can modify this if it's for a city outside of the time zone on your computer (we use tz database time zones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
    - If you give a startdate and/or an enddate, the system will only look at crashes that fall within that date range
    - The crash file is a csv file of crashes that includes (at minimum) columns for latitude, longitude, and date of crashes.
		- Windows users should modify their filepath to use forward slashes (/) rather than the default backslash (\\)
    - The concern files or any other point-based feature files are optional: a csv of concerns that includes (at minimum) a latitude, longitude and date of a concern file.
		- Windows users should modify their filepath to use forward slashes (/) rather than the default backslash (\\)
    - Supplemental files are optional: any number of csv files that contain a lat/lon point and some type of feature you'd like to extract

- Once you have run the initialize_city script, you need to manually edit the configuration file found in e.g. src/config/config_cambridge:
        - If OpenStreetMaps does not have polygon data for your city, the road network will need to be constructed manually. Set the city_latitude and city_longitude values to the centerpoint of the city, and the city_radius to an appropriate distance (in km) that you would like the road network to be built for, e.g 15 for 15km radius from the specified lat / lng.
        - For your csv crash file, enter the column header for id, latitude, longitude, and date.  If time is in a different column than date, give that column header as well. If your csv file does not contain an id field, just put ID here, and the csv will be modified to add an ID
        - If you have any supplemental files, they will be listed under data_source. For each data source, you'll need to enter the column headers for latitude, longitude, and date.
        - Modify time_target to be the last month and year of your crash data (this is legacy and you won't need to do this unless you want to do week-by-week modeling)
- Manually edit config.js in /reports/ to add your mapbox api key (from when you made a mapbox account) as MAPBOX_TOKEN

### Geocoding

- If your crash file provides addresses but not latitude/longitude, you'll need to geocode your crash file before running the pipeline. This can be done from the src directory by running `python -m tools.geocode_batch -d <data directory created from the initalize_city script> -f <crash filename> -a <address field in the crash csv file> -c <city name, e.g. "Boston, Massachusetts, USA"`. If you have a very large number of entries to geocode, you may choose to use mapbox's geocoder instead of google's (the default for this script). In that case, you can also pass in your mapbox token to the script with the -m flag.

### Running on existing cities
- Cities we have already set up will already have a config file.

- Run the pipeline: `python pipeline.py -c <config file>`

## Individual pipeline steps

To learn more about any individual steps (which are themselves often broken up into a number of steps), look at the README in that directory

### 1) Data Standardization

Found in src/data_standardization <br><br>
Cities can provide csv files containing crash and point-based feature data (including, but not limited to concerns).  Due to the varying recording methodologies used across cities, we run this step to turn csv files into compatible JSON files.

2) Data Generation

Found in src/data <br><br>
The data generation steps create a set of maps of road segments for the city, generates features for the road segments, and for each crash, assign it to its nearest road segment.

3) Feature Generation

Found in src/features <br><br>
Documented in the README under src/data/ <br><br>
The feature generation step takes the data from the data generation step, and turns them into a feature set.

4) Training the model

Found in src/models <br><br>

5) Visualizing the results

Found in src/visualization and reports/ <br><br>
The script to generate the datasets needed to power the visualization can be found in src/visualization while the actual files used to display the visualization are found in /reports/.
