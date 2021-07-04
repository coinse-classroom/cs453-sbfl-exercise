from inspect import getmembers, isfunction
from importlib import import_module
from coverage import Coverage
import pytest
import sys
import os
import glob
import json

def get_total_coverage(target_file, test_file):

    target_dir = os.path.split(target_file)[0]
    cov = Coverage(source=[target_dir], omit=[test_file])
    cov.erase()

    cov.start()
    old_out = sys.stdout
    old_err = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')  

    test_name = os.path.basename(test_file)
    test_name = os.path.splitext(test_name)[0]
    pytest.main([f"{test_file}", "--cache-clear"])

    sys.stdout = old_out
    sys.stderr = old_err
    cov.stop()

    out_filename = f"{test_file}_cov.json"
    
    cov.json_report(morfs=[target_file], outfile=out_filename)
    json_str = "".join(open(out_filename, "r").readlines())
    decoder = json.JSONDecoder()        
    coverage = decoder.decode(json_str)
    os.remove(out_filename)
    return coverage["files"][target_file]

def get_test_method_result(target_file, test_file, test_method_name):

    target_dir = os.path.split(target_file)[0]
    cov = Coverage(source=[target_dir], omit=[test_file])
    cov.erase()  # erase previously collected data

    cov.start()  # start coverage collection

    old_out = sys.stdout   # do not mess up stdout with coverage.py output
    old_err = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w') 

    test_name = os.path.basename(test_file)
    test_name = os.path.splitext(test_name)[0]
    
    ret = pytest.main([f"{test_file}::{test_method_name}", "--cache-clear"])


    cov.stop()  # stop coverage collection
    sys.stdout = old_out
    sys.stderr = old_err

    # save and load JSON report of coverage collection
    tmp_filename = "tmp_total_cov.json"

    cov.json_report(morfs=[target_file], outfile=tmp_filename)

    json_str = "".join(open(tmp_filename, "r").readlines())
    decoder = json.JSONDecoder()        
    coverage = decoder.decode(json_str)
    os.remove(tmp_filename)

    return ret == pytest.ExitCode.OK, coverage["files"][target_file]

def get_test_methods(pytest_file):
    test_name = os.path.splitext(pytest_file)[0]
    test_name = test_name.replace("/", ".")
    module = import_module(test_name)
    return getmembers(module, isfunction)