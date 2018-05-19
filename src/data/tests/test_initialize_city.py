import os
import subprocess
import json
import shutil


def test_initialize_city_should_run_successfully(tmpdir):

    # Copy test data into temp directory
    orig_path = os.path.dirname(
        os.path.abspath(__file__)) + '/data/'
    path = tmpdir.strpath + '/data/'
    raw_files_path = path + 'raw/'
    shutil.copytree(orig_path, path)

    #other constants that the test needs to pass in
    new_city_folder = '/new_city'

    #create a config folder in temp directory prior to running the test
    if not os.path.exists(tmpdir.strpath+"config/"):
        print "no config dir, creating one..."
        os.makedirs(tmpdir.strpath+"/config/")
        os.makedirs(tmpdir.strpath+"/reports/")
    
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
        raw_files_path+'Crashes_new_city.csv',
        '-concern',
        raw_files_path+'Concerns_new_city.csv',
        '-f',
        new_city_folder,
    ])