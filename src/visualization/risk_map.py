"""
Title: risk_map.py
 
Author: @bpben, @alicefeng

This script generates a map of the "risk estimates" from model predictions.  
 
Usage:
    --modelname: name of the models
            these will be used as the name of the layers in the map so they must be unique
    --city: name of the city the predictions are for
    --normalize: optional flag to indicate it predictions need to be normalized

Inputs:
    config file for city to get the coordinates to center the map on
    csv files of model predictions
    inter_and_non_int.shp - a Shapefile with both intersection and non-intersection segments and their segment_ids
    
Output:
    risk_map.html - a Leaflet map with model predictions visualized on it
"""

import pandas as pd
import geopandas as gpd
import folium
import branca.colormap as cm
import argparse
import yaml
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))))

DATA_FP = '/processed/'
MAP_FP = '/processed/maps/'
CONFIG_FP = BASE_DIR + '/src/config/'

# parse arguments
parser = argparse.ArgumentParser(description="Plot crash predictions on a map")
parser.add_argument("-m", "--modelname", nargs="+",
                    help="name of the model, must be unique")
parser.add_argument("-c", "--city", nargs=1, 
                    help="name of the city the model is for, must match name of its data folder")
#parser.add_argument("-f", "--filename", nargs="+",
#                    help="name of the file with the predictions to be plotted on the map, must specify at least 1")
#parser.add_argument("-c", "--colname", nargs="+",
#                    help="column name that has the predictions, must be specified in the same order as the filenames")
parser.add_argument("-n", "--normalize", help="normalize predictions", action="store_true")
args = parser.parse_args()

# zip filenames and column names
#if len(args.modelname) == len(args.filename) == len(args.colname):
#    match = zip(args.modelname, args.filename, args.colname)
#else:
#    raise Exception("Number of models, files and column names must match")


def process_data(city):
        """Preps model output for plotting on a map

        Reads in model output and filters to non-zero predictions.
        Spatially joins the data to a shapefile of the specified city's road network to match segments with
        their predicted crash risk.
        Normalizes the predictions if needed.

        Args:
            city: name of the city the predictions are for
            
        Returns:
            a dataframe that links segment_ids, predictions and spatial geometries
        """
        output = pd.read_csv(BASE_DIR + '/data/' + city + DATA_FP + 'seg_with_predicted.csv', dtype={'segment_id':'str'})

        # filter dataframe to only seg with risk>0 to reduce size
        output = output[output['prediction']>0]

        # filter dataframe down to only one week of predictions
        output = output[output['week']==51]
       
        # Merge on model results to the GeoDataframe
        streets_w_risk = streets.merge(output, left_on='id',right_on='segment_id')

        # normalize predictions if specified
        if args.normalize:
            print "Normalizing predictions..."
            streets_w_risk['prediction'] = streets_w_risk['prediction'] / streets_w_risk['prediction'].max()

        return streets_w_risk

def add_layer(dataset, modelname, mapname):
        """Plots predictions on a Leaflet map

        Args:
            dataset: a dataframe with the data to be plotted
            modelname: name of the model to be used as the layer name
            mapname: name of the map to be plotted on

        Returns:
            a GeoJSON layer added to the map
        """
        folium.GeoJson(dataset,
                       name=modelname,
                       style_function=lambda feature: {
                               'color': color_scale(feature['properties']['prediction'])
                               }).add_to(mapname)

        
# Read in shapefile as a GeoDataframe
city = args.city[0]

streets = gpd.read_file(BASE_DIR + '/data/' + city + MAP_FP + 'inter_and_non_int.shp')

# Set the projection as EPSG:3857 since the shapefile didn't export with one
streets.crs = {'init': 'epsg:3857'}

# Then reproject to EPSG:4326 to match what Leaflet uses
streets = streets.to_crs({'init': 'epsg:4326'})


### Make map

# First create basemap

# parse coordinates from yaml file for the city
with open(CONFIG_FP + 'config_' + city + '.yml') as f:
    config = yaml.safe_load(f)

city_lat = config['city_latitude']
city_long = config['city_longitude']

city_map = folium.Map([city_lat, city_long], tiles='Cartodb dark_matter', zoom_start=12)
folium.TileLayer('Cartodb Positron').add_to(city_map)

# Create style function to color segments based on their risk score
#color_scale = cm.linear.YlOrRd.scale(0, 1)
color_scale = cm.LinearColormap(['yellow', 'orange', 'red'], vmin=0., vmax=1.)
#color_scale = cm.linear.YlOrRd.scale(streets_w_risk[args.colname].min(), 
#                                     streets_w_risk[args.colname].max())

# Plot model predictions as separate layers
for model in args.modelname:
    predictions = process_data(city)
    add_layer(predictions, model, city_map)

# Add control to toggle between model layers
folium.LayerControl(position='bottomright').add_to(city_map)

# Finally, add legend
color_scale.caption = "Risk Score"
city_map.add_child(color_scale)

# Save map as separate html file
city_map.save('risk_map.html')
