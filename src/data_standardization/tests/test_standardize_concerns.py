from jsonschema import validate
import json
import os
import subprocess
import shutil

TEST_FP = os.path.dirname(os.path.abspath(__file__))

def test_boston_vision_zero_concerns(tmpdir):
    """
    Confirm that standardize concerns script produces correct schema after transformation of Vision Zero Concerns
    """
    data_path_here = os.path.dirname(
        os.path.abspath(__file__)) + '/data/raw/concerns/'

    # copy over concerns csv to tmpDir for test
    tmp_copy_location = tmpdir.strpath + '/raw/concerns/'
    shutil.copytree(data_path_here, tmp_copy_location)
    os.makedirs(tmpdir.strpath+'/standardized/')

    # Call standardize_concerns
    subprocess.check_call([
        'python',
        '-m',
        'data_standardization.standardize_concerns',
        '-d',
        'boston',
        '-f',
        tmpdir.strpath
    ])

    with open(tmpdir.strpath+'/standardized/concerns.json') as f:
        test_concerns = json.load(f)

    # verify schema of output file generated
    validate(test_concerns, json.load(open(
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                     "standards", "concerns-schema.json"))))

def test_boston_see_click_fix_concerns(tmpdir):
    """
    Confirm that standardize concerns script produces correct schema after transformation of See Click Fix Concerns
    """
    data_path_here = os.path.dirname(
        os.path.abspath(__file__)) + '/data/raw/concerns/'

    # copy over concerns csv to tmpDir for test
    tmp_copy_location = tmpdir.strpath + '/raw/concerns/'
    shutil.copytree(data_path_here, tmp_copy_location)
    os.makedirs(tmpdir.strpath+'/standardized/')

    # Call standardize_concerns
    subprocess.check_call([
        'python',
        '-m',
        'data_standardization.standardize_concerns',
        '-d',
        'boston',
        '-f',
        tmpdir.strpath
    ])

    with open(tmpdir.strpath+'/standardized/concerns.json') as f:
        test_concerns = json.load(f)

    # verify schema of output file generated
    validate(test_concerns, json.load(open(
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                     "standards", "concerns-schema.json"))))
