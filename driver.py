from coverage import Coverage
from inspect import getmembers, isfunction
from importlib import import_module
import pytest
import os
import glob
import argparse
import sys
import json

parser = argparse.ArgumentParser(description='Spectrum Based Fault Localisation')
parser.add_argument("-s", "--source_dir", required=True,
                    help='the directory that contains Python source files')
parser.add_argument("-f", "--target_file", required=True,
                    help='the file to apply SBFL analysis')
parser.add_argument('-t', "--test_dir", required=True,
                    help='the directory that contains PyTest test files (test_*.py)')

args = parser.parse_args()

target_file = args.target_file
test_dir = args.test_dir
test_files = glob.glob(os.path.join(test_dir, "test_*.py"))
test_names = []
test_results = {}
test_traces = {}

cov = Coverage(source=["."], omit=test_files)
for test_file in test_files:
    test_file = test_file[2:-3]
    module = import_module(test_file)
    members = getmembers(module, isfunction)
    for member in members:
        test_name = member[0]
        test_names.append(test_name)
        cov.start()
        
        old_out = sys.stdout
        old_err = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        test_result = pytest.main([f"{test_file}.py::{test_name}"])
        sys.stdout = old_out
        sys.stderr = old_err
        
        cov.stop()
        out_filename = f"{test_name}_cov.json"
        cov.json_report(morfs=[target_file], outfile=out_filename)

        json_str = "".join(open(out_filename, "r").readlines())
        decoder = json.JSONDecoder()
        coverage = decoder.decode(json_str)
        test_results[test_name] = test_result==pytest.ExitCode.OK
        test_traces[test_name] = coverage["files"][target_file]["executed_lines"]

print(test_results)
print(test_traces)

    
