# Standardize a crashes CSV into compatible JSON document.
# Author terryf82 https://github.com/terryf82

import argparse
import os
import pandas as pd
from pandas.io.json import json_normalize
from collections import OrderedDict
import csv
import calendar
import random
import dateutil.parser as date_parser
from .standardization_util import parse_date, validate_and_write_schema
from shapely.geometry import Point
import geopandas as gpd
from data.util import read_geocode_cache
import data.config

CURR_FP = os.path.dirname(
    os.path.abspath(__file__))
BASE_FP = os.path.dirname(os.path.dirname(CURR_FP))

def read_standardized_fields(raw_crashes, fields, opt_fields,
                             timezone, datadir, city,
                             startdate=None, enddate=None):

    crashes = {}
    # Drop times from startdate/enddate in the unlikely event
    # they're passed in
    if startdate:
        startdate = parse_date(startdate, timezone)
        startdate = date_parser.parse(startdate).date()
    if enddate:
        enddate = parse_date(enddate, timezone)
        enddate = date_parser.parse(enddate).date()

    min_date = None
    max_date = None
    
    cached_addresses = {}

    if (not fields['latitude'] or not fields['longitude']):
        if 'address' in opt_fields and opt_fields['address']:
            # load cache for geocode lookup
            geocoded_file = os.path.join(
                    datadir, 'processed', 'geocoded_addresses.csv')
            if os.path.exists(geocoded_file):
                cached_addresses = read_geocode_cache(
                    filename=os.path.join(
                        datadir, 'processed', 'geocoded_addresses.csv'))
            else:

                raise SystemExit(
                    "Need to geocode addresses before standardizing crashes")
        else:
            raise SystemExit(
                "Can't standardize crash data, no lat/lon or address found"
            )

    no_geocoded_count = 0
    for i, crash in enumerate(raw_crashes):
        if i % 10000 == 0:
            print(i)
            
        lat = crash[fields['latitude']] if fields['latitude'] else None
        lon = crash[fields['longitude']] if fields['longitude'] else None

        if not lat or not lon:

            # skip any crashes that don't have coordinates
            if 'address' not in opt_fields or opt_fields['address'] not in crash:
                continue

            address = crash[opt_fields['address']] + ' ' + city

            # If we have an address, look it up in the geocoded cache
            if address in cached_addresses:
                address, lat, lon, _ = cached_addresses[address]
                if not address:
                    no_geocoded_count += 1
                    continue
            else:
                no_geocoded_count += 1
                continue

        # construct crash date based on config settings, skipping any crashes without date
        if fields["date_complete"]:
            if not crash[fields["date_complete"]]:
                continue

            else:
                crash_date = crash[fields["date_complete"]]

        elif fields["date_year"] and fields["date_month"]:
            if fields["date_day"]:
                crash_date = str(crash[fields["date_year"]]) + "-" + str(
                    crash[fields["date_month"]]) + "-" + crash[fields["date_day"]]
            # some cities do not supply a day of month for crashes, randomize if so
            else:
                available_dates = calendar.Calendar().itermonthdates(
                    crash[fields["date_year"]], crash[fields["date_month"]])
                crash_date = str(random.choice(
                    [date for date in available_dates if date.month == crash[fields["date_month"]]]))

        # skip any crashes that don't have a date
        else:
            continue

        crash_time = None
        if fields["time"]:
            crash_time = crash[fields["time"]]

        if fields["time_format"]:
            crash_date_time = parse_date(
                crash_date,
                timezone,
                crash_time,
                fields["time_format"]
            )

        else:
            crash_date_time = parse_date(
                crash_date,
                timezone,
                crash_time
            )

        # Skip crashes where date can't be parsed
        if not crash_date_time:
            continue

        crash_day = date_parser.parse(crash_date_time).date()
        # Drop crashes that occur outside of the range, if specified
        if ((startdate is not None and crash_day < startdate) or
                (enddate is not None and crash_day > enddate)):

            continue
        if min_date is None or crash_day < min_date:
            min_date = crash_day
        if max_date is None or crash_day > max_date:
            max_date = crash_day
        
        formatted_crash = OrderedDict([
            ("id", crash[fields["id"]]),
            ("dateOccurred", crash_date_time),
            ("location", OrderedDict([
                ("latitude", float(lat)),
                ("longitude", float(lon))
            ]))
        ])
        formatted_crash = add_city_specific_fields(crash, formatted_crash,
                                                   opt_fields)
        crashes[formatted_crash["id"]] = formatted_crash

    if min_date and max_date:
        print("Including crashes between {} and {}".format(
            min_date.isoformat(), max_date.isoformat()))
    elif min_date:
        print("Including crashes after {}".format(
            min_date.isoformat()))
    elif max_date:
        print("Including crashes before {}".format(
            max_date.isoformat()))

    # Making sure we have enough entries with lat/lon to continue
    if len(crashes) > 0 and no_geocoded_count/len(raw_crashes) > .9:
        raise SystemExit("Not enough geocoded addresses found, exiting")
    
    return crashes


def add_city_specific_fields(crash, formatted_crash, fields):

    # Add summary and address
    if "summary" in list(fields.keys()) and fields["summary"]:
        formatted_crash["summary"] = crash[fields["summary"]]
    if "address" in list(fields.keys()) and fields["address"]:
        formatted_crash["address"] = crash[fields["address"]]

    # setup a vehicles list for each crash
    formatted_crash["vehicles"] = []

    # check for car involvement
    if "vehicles" in list(fields.keys()) and fields["vehicles"] == "mode_type":
        # this needs work, but for now any of these mode types
        # translates to a car being involved, quantity unknown
        if crash[fields["vehicles"]] == "mv" or crash[fields["vehicles"]] == "ped" or crash[fields["vehicles"]] == "":
            formatted_crash["vehicles"].append({"category": "car"})

    elif "vehicles" in list(fields.keys()) and fields["vehicles"] == "TOTAL_VEHICLES":
        if crash[fields["vehicles"]] != 0 and crash[fields["vehicles"]] != "":
            formatted_crash["vehicles"].append({
                "category": "car",
                "quantity": int(crash[fields["vehicles"]])
            })

    # check for bike involvement
    if "bikes" in list(fields.keys()) and fields["bikes"] == "mode_type":
        # assume bike and car involved, quantities unknown
        if crash[fields["bikes"]] == "bike":
            formatted_crash["vehicles"].append({"category": "car"})
            formatted_crash["vehicles"].append({"category": "bike"})

    elif "bikes" in list(fields.keys()) and fields["bikes"] == "TOTAL_BICYCLES":
        if crash[fields["bikes"]] != 0 and crash[fields["bikes"]] != "":
            formatted_crash['vehicles'].append({
                "category": "bike",
                "quantity": int(crash[fields["bikes"]])
            })
    return formatted_crash


def add_id(csv_file, id_field):
    """
    If the csv_file does not contain an id, create one
    """

    rows = []
    with open(csv_file) as f:
        csv_reader = csv.DictReader(f)
        count = 1
        for row in csv_reader:
            if id_field in row:
                break
            row.update({id_field: count})
            rows.append(row)
            count += 1
    if rows:
        with open(csv_file, 'w') as f:
            writer = csv.DictWriter(f, list(rows[0].keys()))
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

def calculate_crashes_by_location(df):
    """
    Calculates total number of crashes that occurred at each unique lat/lng pair and
    generates a comma-separated string of the dates that crashes occurred at that location

    Inputs:
        - a dataframe where each row represents one unique crash incident

    Output:
        - a dataframe with the total number of crashes at each unique crash location
          and list of unique crash dates
    """
    crashes_agg = df.groupby(['latitude', 'longitude']).agg(['count', 'unique'])
    crashes_agg.columns = crashes_agg.columns.get_level_values(1)
    crashes_agg.rename(columns={'count': 'total_crashes', 'unique': 'crash_dates'}, inplace=True)
    crashes_agg.reset_index(inplace=True)
    
    crashes_agg['crash_dates'] = crashes_agg['crash_dates'].str.join(',')
    return crashes_agg

def make_crash_rollup(crashes_json):
    """
    Generates a GeoDataframe with the total number of crashes and a comma-separated string
    of crash dates per unique lat/lng pair

    Inputs:
        - a json of standardized crash data

    Output:
        - a GeoDataframe with the following columns:
            - total number of crashes
            - list of unique dates that crashes occurred
            - GeoJSON point features created from the latitude and longitude
    """
    df_std_crashes = json_normalize(crashes_json)
    df_std_crashes = df_std_crashes[["dateOccurred", "location.latitude", "location.longitude"]]
    df_std_crashes.rename(columns={"location.latitude": "latitude", "location.longitude": "longitude"}, inplace=True)

    crashes_agg = calculate_crashes_by_location(df_std_crashes)
    crashes_agg["coordinates"] = list(zip(crashes_agg.longitude, crashes_agg.latitude))
    crashes_agg["coordinates"] = crashes_agg["coordinates"].apply(Point)
    crashes_agg = crashes_agg[["coordinates", "total_crashes", "crash_dates"]]

    crashes_agg_gdf = gpd.GeoDataFrame(crashes_agg, geometry="coordinates")
    print(crashes_agg_gdf.columns)
    return crashes_agg_gdf

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, required=True,
                        help="config file")
    parser.add_argument("-d", "--datadir", type=str, required=True,
                        help="data directory")

    args = parser.parse_args()

    # load config
    config_file = args.config
    config = data.config.Configuration(config_file)

    crash_dir = os.path.join(args.datadir, "raw/crashes")
    if not os.path.exists(crash_dir):
        raise SystemExit(crash_dir + " not found, exiting")

    print("searching "+crash_dir+" for raw files:")
    dict_crashes = {}

    for csv_file, csv_config in config.crashes_files.items():
        if not os.path.exists(os.path.join(crash_dir, csv_file)):
            raise SystemExit(os.path.join(
                crash_dir, csv_file) + " not found, exiting")

        add_id(
            os.path.join(crash_dir, csv_file), csv_config['required']['id'])

        print("processing {}".format(csv_file))

        df_crashes = pd.read_csv(os.path.join(
            crash_dir, csv_file), na_filter=False)
        raw_crashes = df_crashes.to_dict("records")

        std_crashes = read_standardized_fields(
            raw_crashes,
            csv_config['required'],
            csv_config['optional'],
            config.timezone,
            args.datadir,
            config.city,
            config.startdate,
            config.enddate
        )

        print("{} crashes loaded with standardized fields, checking for specific fields".format(
            len(std_crashes)))
        dict_crashes.update(std_crashes)

    print("{} crashes loaded, validating against schema".format(len(dict_crashes)))

    schema_path = os.path.join(BASE_FP, "standards", "crashes-schema.json")
    list_crashes = list(dict_crashes.values())
    crashes_output = os.path.join(args.datadir, "standardized/crashes.json")
    validate_and_write_schema(schema_path, list_crashes, crashes_output)

    crashes_agg_gdf = make_crash_rollup(list_crashes)

    crashes_agg_path = os.path.join(args.datadir, "standardized/crashes_rollup.geojson")
    if os.path.exists(crashes_agg_path):
        os.remove(crashes_agg_path)
    crashes_agg_gdf.to_file(os.path.join(args.datadir, "standardized/crashes_rollup.geojson"), driver="GeoJSON")

