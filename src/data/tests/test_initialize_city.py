import os
import subprocess
import json
import shutil
import yaml
import py


def test_initialize_city_should_run_successfully(tmpdir):
    # Copy test data into temp directory
    orig_path = os.path.dirname(
        os.path.abspath(__file__)) + '/data/'
    path = os.path.join(tmpdir.strpath, 'data')
    raw_files_path = os.path.join(path, 'test_initialize_city')
    shutil.copytree(orig_path, path)

    # other constants that the test needs to pass in
    new_city_folder = 'new_city'

    # create a config folder in temp directory prior to running the test
    if not os.path.exists(os.path.join(tmpdir.strpath, 'config')):
        print("no config dir, creating one...")
        os.makedirs(os.path.join(tmpdir.strpath, 'config'))
        os.makedirs(os.path.join(tmpdir.strpath, 'reports'))

    subprocess.check_call([
        'python',
        '-m',
        'initialize_city',
        '-city',
        'new_city',
        '-basePath',
        tmpdir.strpath,
        '-configPath',
        os.path.join(tmpdir.strpath, 'config/'),
        '-crash',
        os.path.join(raw_files_path, 'Crashes_new_city.csv'),
        '-concern',
        os.path.join(raw_files_path, 'Concerns_new_city.csv'),
        '-f',
        new_city_folder
    ])


def test_make_js_config(monkeypatch):
    assert True

def test_initialize_city_brisbane(monkeypatch):
    def mockreturn(address):
        return "Brisbane, Australia", -27.4697707, 153.0251235, 'S'

    monkeypatch.setattr(initialize_city, 'geocode_address', mockreturn)
    tmpdir = py.path.local('/tmp')

    # Generate a test config for Brisbane
    initialize_city.make_config_file(
        tmpdir.join('/test_config_brisbane.yml'),
        'Brisbane, Australia',
        'brisbane',
        'test_crashes.csv',
        'test_concerns.csv'
    )

    # check that the file contents generated is identical to a pre-built string
    expected_file_contents = """# City name
city: Brisbane, Australia
# City centerpoint latitude & longitude (default geocoded values set)
city_latitude: -27.4697707
city_longitude: 153.0251235
# Radius of city's road network from centerpoint in km, required if OSM has no polygon data (defaults to 20km)
city_radius: 20
# The folder under data where this city's data is stored
name: brisbane
# If given, limit crashes to after start_year and before end_year
# Recommended to limit to just a few years for now
start_year: 
end_year: 


#################################################################
# Configuration for data standardization

# crash file configurations
crashes_files:
  test_crashes.csv:
    required:
      id: 
      latitude: 
      longitude: 
      # If date supplied in single column:
      date_complete: 
      # If date is separated into year/month/day:
      date_year: 
      date_month: 
      # Leave date_day empty if not available
      date_day: 
      # If time is available and separate from date:
      time: 
      # If time specified, time_format is one of:
      # default (HH:MM:SS)
      # seconds (since midnight)
      # military (HHMM)
      time_format: 
    optional:
      summary: 
      address: 
      vehicles: 
      bikes: 

# List of concern type information
concern_files:
  - name: concern
      filename: test_concerns.csv
      latitude: 
      longitude: 
      time: 


# week on which to predict crashes (week, year)
# Best practice is to choose a week towards the end of your crash data set
# in format [month, year]
time_target: [30, 2017]
# specify how many weeks back to predict in output of train_model
weeks_back: 1"""

    with open(tmpdir.join('/test_config_brisbane.yml'), 'r') as test_file:
        test_file_contents = test_file.read()

    assert test_file_contents == expected_file_contents
