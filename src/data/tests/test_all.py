import os
import subprocess
import json
import shutil


def test_all(tmpdir):

    # Copy test data into temp directory
    orig_path = os.path.dirname(
        os.path.abspath(__file__)) + '/data/'
    path = tmpdir.strpath + '/data/'
    new_city_folder = '/brishport'
    raw_files_path = path + 'raw/'
    #copy everything in src/data/tests/data to tmpdir/data
    shutil.copytree(orig_path, path)
    filename = raw_files_path + 'Boston_Segments.shp'

    # subprocess.check_call([
    #     'python',
    #     '-m',
    #     'data.extract_intersections',
    #     filename,
    #     '-d',
    #     path
    # ])

    # subprocess.check_call([
    #     'python',
    #     '-m',
    #     'data.create_segments',
    #     '-d',
    #     path,
    # ])

    # subprocess.check_call([
    #     'python',
    #     '-m',
    #     'data.join_segments_crash_concern',
    #     '-d',
    #     path,
    # ])


    print "curr dir is... " + tmpdir.strpath
    if not os.path.exists(tmpdir.strpath+"config/"):
        print "no config dir, creating one..."
        os.makedirs(tmpdir.strpath+"/config/")

    if os.path.exists(tmpdir.strpath+"/config/"):
        print "config dir was created with path ..." + tmpdir.strpath+"/config/"
    subprocess.check_call([
        'python',
        '-m',
        'initialize_city',
        '-city',
        'Brishport',
        '-basePath',
        tmpdir.strpath,
        '-configPath',
        tmpdir.strpath+'/config',
        '-crash',
        raw_files_path+'Crashes_Brishport.csv',
        '-concern',
        raw_files_path+'Concerns_Brishport.csv',
        '-f',
        new_city_folder,
    ])
    # data = json.load(open(path + '/processed/crash_joined.json'))
    # assert data[0]['near_id'] == 2

    # data = json.load(open(path + '/processed/concern_joined.json'))
    # assert data[0]['near_id'] == 3


