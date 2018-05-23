import argparse
import os
import shutil
import sys
from data.util import geocode_address


#We now pass base path and config path through the call to initialize_city.
#Hence BASE_DIR should be passed from the caller instead.
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)))


def make_config_file(yml_file, city, folder, crash, concern):
    f = open(yml_file, 'w+')

    f.write(
        "# City name\n" +
        "city: {}\n".format(city) +
        "# The folder under data where this city's data is stored\n" +
        "name: {}\n".format(folder) +
        "# If given, limit crashes to after start_year and before end_year\n" +
        "# Recommended to limit to just a few years for now\n" +
        "start_year: \n" +
        "end_year: \n\n\n" +
        "#################################################################\n" +
        "# Configuration for data standardization\n\n" +
        "# crash file configurations\n" +
        "crashes_files:\n" +
        "  {}:\n".format(crash) +
        "    required:\n" +
        "      id: \n" +
        "      latitude: \n" +
        "      longitude: \n" +
        "      date: \n" +
        "      # Time is only required if date and time" +
        " are in different columns\n" +
        "      time: \n" +
        "    optional:\n" +
        "      summary: \n" +
        "      address: \n\n"
    )

    if concern:
        f.write(
            "# List of concern type information" +
            "concern_files:\n" +
            "- name: concern\n" +
            "filename: {}\n".format(concern) +
            "latitude: \n" +
            "longitude: \n" +
            "time: \n\n\n"
        )
    f.write(
        "# week on which to predict crashes (week, year)\n" +
        "# Best practice is to choose a week towards the end of your crash data set\n" +
        "# in format [month, year]\n" +
        "time_target: [30, 2017]\n" + 
        "# specify how many weeks back to predict in output of train_model\n"+
        "weeks_back: 1"
    )
    f.close()
    print "Wrote new configuration file in {}".format(yml_file)


def make_js_config(jsfile, city, folder):
    address = geocode_address(city)

    f = open(jsfile, 'w')
    f.write(
        'var config = {\n' +
        '    MAPBOX_TOKEN: "",\n' +
        '    cities: [\n' +
        '        {\n' +
        '            name: "{}",\n'.format(city) +
        '            id: "{}",\n'.format(folder) +
        '            latitude: {},\n'.format(str(address[1])) +
        '            longitude: {},\n'.format(str(address[2])) +
        '        }\n' +
        '    ]\n' +
        '}\n'
    )
    f.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-city", "--city", type=str, required=True,
                        help="city name")
    parser.add_argument("-f", "--folder", type=str, required=True,
                        help="folder name")
    parser.add_argument('-crash', '--crash_file', type=str, required=True,
                        help="crash file path")
    parser.add_argument('-concern', '--concern_file', type=str,
                        help="concern file path")
    parser.add_argument('-basePath', '--base_path', type=str,
                        help="base file path")
    parser.add_argument('-configPath', '--config_path', type=str,
                        help="base file path")
    args = parser.parse_args()

    if not args.city:
        print "city required"
        sys.exit()
    if not args.folder:
        print "folder required"
        sys.exit()
    if not args.crash_file:
        print "crash file required"
        sys.exit()
    if not args.base_path:
        print "base path for files required"
        sys.exit()
    if not args.config_path:
        print "config path for files required"
        sys.exit()        

    DATA_FP = os.path.join(args.base_path, 'data', args.folder)
 

    crash = args.crash_file.split('/')[-1]
    crash_dir = os.path.join(DATA_FP, 'raw', 'crashes')
    concern = None
    if args.concern_file:
        concern = args.concern_file.split('/')[-1]

    # Check to see if the directory exists
    # if it does, it's already been initialized, so do nothing
    if not os.path.exists(DATA_FP):
        print "Making directory structure under " + DATA_FP
        os.makedirs(DATA_FP)
        os.makedirs(os.path.join(DATA_FP, 'raw'))
        os.makedirs(crash_dir)
        concern_dir = os.path.join(DATA_FP, 'raw', 'concerns')
        os.makedirs(concern_dir)
        os.makedirs(os.path.join(DATA_FP, 'processed'))
        os.makedirs(os.path.join(DATA_FP, 'standardized'))
        shutil.copyfile(args.crash_file, os.path.join(crash_dir, crash))

        if args.concern_file:
            shutil.copyfile(args.concern_file, os.path.join(
                concern_dir, concern))

    else:
        print args.folder + " already initialized, skipping"

    #the actual call should pass in 'src/config/config_'
    yml_file = os.path.join(
        args.config_path ,'config_' +args.folder + '.yml')
    print "yml path is: " + yml_file

    if not os.path.exists(yml_file):
        make_config_file(yml_file, args.city, args.folder, crash, concern)

    js_file = os.path.join(
        args.base_path, 'reports/config.js')
    if not os.path.exists(js_file):
        print "Writing config.js"
        make_js_config(js_file, args.city, args.folder)
