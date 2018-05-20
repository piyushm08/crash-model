import os
import subprocess
import json
import shutil

#This is still a work in progress. Code might be incomplete/not working.
def test_entire_pipeline_should_run_without_errors(tmpdir):

    # Copy test data into temp directory
    orig_path = os.path.dirname(
        os.path.abspath(__file__)) + '/data/'
    path = tmpdir.strpath + '/data/'
    raw_files_path = path + '/test_pipeline/'
    
    #copy over data needed for test inside tmpDir
    shutil.copytree(orig_path+'/test_pipeline/', path+'/test_pipeline/')
    
    city_level_data_path = path+'/boston'+'/standardized/'
    if not os.path.exists(city_level_data_path):
        print "no dir for city level data, creating one in " + path
        shutil.copytree(orig_path+'/standardized/', city_level_data_path)
        
    subprocess.check_call([
        'python',
        '-m',
        'pipeline',
        '-b',
        tmpdir.strpath,
        '--config_file',
        path+'/test_pipeline/config_boston.yml',
    ])