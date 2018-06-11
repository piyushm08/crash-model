# Crash model visualization

This directory contains the code that generates the data needed for the visualization found in `/reports/` as well as utilities to aid with exploring data.

## Generating the data for visualization in `/reports/`

####make\_viz\_data.py
This script is part of the pipeline process that automatically generates the datasets needed for the final visualization. It outputs three files into the /reports/ directory:

* crashes.geojson
* preds.json
* weekly_crashes.csv


## Visualization Utilities

####risk_map.py 
This script can plot predictions generated from multiple models on a Leaflet map.  It color-codes each segment based on the magnitude of the predicted risk.

To run this script, you need the following inputs:
- inter_and_non_int.shp (created in create_segments.py)
- csv files of predictions which conform to the predictions data standard 

The script takes the following flag arguments on the command line:

-m = model names (these will be the names of the layers on your map)

-f = csv file names (one for each model and specified in the same order as the model names)

-n = optional flag to indicate if predictions need to be normalized

An example of how to run this script to plot the output from two models is as follows:
```
python risk_map.py -m model1 model2 -f model1_output.csv model2_output.csv
```

####plot_points.py 
This script can be used to plot point-level data on a Leaflet map.

To run this script, you need the following inputs:
- csv files of point-level data (there should separate columns named "X" and "Y" for the X and Y coordinates)

The script takes the following flag arguments on the command line:

-n = name of the data to be plotted (these will be the names of the layers on your map)

-f = csv file names (one for each set of data and specified in the same order as the layer names)

-lat = latitude of the city you are mapping

-lon = longitude of the city you are mapping

-dir = filepath of the directory the data you want to map is stored in

An example of how to run this script is as follows:
```
python plot_points.py -n crashes -f cad_crash_events.csv -lat 42.36 -lon -71.05 -dir /full/file/path/to/your/dataset/
```