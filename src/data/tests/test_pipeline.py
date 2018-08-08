import os
import subprocess
import json
import shutil

#This is still a work in progress. Code might be incomplete/not working.
def test_entire_pipeline_should_run_without_errors(tmpdir):

    # Copy test data into temp directory
    orig_path = os.path.dirname(
        os.path.abspath(__file__)) + '/data/'
    tmp_orig_path = tmpdir.strpath + '/test_pipeline/'

    #copy over data needed for test inside tmpDir
    shutil.copytree(orig_path+'/test_pipeline/', tmp_orig_path)
    
    boston_path = tmp_orig_path+'data/boston/'

    #/tmpStrPath/test_pipeline_- config.yml
    #/tmpStrPath/test_pipeline/data/boston/standardized
    #/tmpStrPath/test_pipeline/data/boston/raw has data corresponding to src/data/tests/data/raw
    city_level_data_path_standardized = boston_path +'standardized'
    city_level_data_path_raw = boston_path +'raw'
    city_level_data_path_processed = boston_path +'processed'

    os.makedirs(city_level_data_path_standardized)

    #orig path is current_directory/data/
    shutil.copytree(orig_path+'/raw/', city_level_data_path_raw)
    shutil.copytree(orig_path+'/boston/processed/', city_level_data_path_processed)

    #tmp_orig_path is test_dir+'/test_pipeline/'
    #config file is test_dir+'/test_pipeline/config_boston.yml
    #raw and processed data is in  test_dir+'/test_pipeline/data/boston/raw and
    #test_dir+'/test_pipeline/data/boston/processed
    subprocess.check_call([
        'python',
        '-m',
        'pipeline',
        '-b',
        tmp_orig_path,
        '--config_file',
        tmp_orig_path+'config_boston.yml',
        '--onlysteps',
        'generation, standardization,model'
    ])