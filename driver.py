from coverage import Coverage
from inspect import getmembers, isfunction
from importlib import import_module
from scipy.stats import rankdata
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
covered_lines = []

def generate_spectrum(test_traces, test_results):
    spectrum = []
    for line in sorted(covered_lines):
        e_p, e_f, n_p, n_f = 0, 0, 0, 0
        for test_name in test_names:
            trace = test_traces[test_name]
            result = test_results[test_name]
            if line in trace["executed_lines"] and result:
                e_p += 1
            elif line in trace["executed_lines"] and not result:
                e_f += 1
            elif line not in trace["executed_lines"] and result:
                n_p += 1
            elif line not in trace["executed_lines"] and not result:
                n_f += 1
        spectrum.append((line, (e_p, e_f, n_p, n_f)))
    return spectrum

def op2(spectrum):
    scores = []
    for s in spectrum:
        line, (e_p, e_f, n_p, n_f) = s
        scores.append((line, e_f - e_p / (e_p + n_p + 1.0)))
    return scores

def tarantula(spectrum):
    scores = []
    for s in spectrum:
        line, (e_p, e_f, n_p, n_f) = s
        if e_f == 0:
            scores.append((line, 0.0))
        else:
            scores.append((line, (e_f / (e_f + n_f)) / ((e_f / (e_f + n_f)) + (e_p / (e_p + n_p)))))
    return scores


def ranking(scores):
    lines = [x[0] for x in scores]
    raw_scores = [x[1] for x in scores]
    ranks = len(raw_scores) - rankdata(raw_scores, method="max").astype(int)
    return list(zip(lines, ranks))

cov = Coverage(source=["."], omit=test_files)

for test_file in test_files:
    test_file = test_file[2:-3]
        
    # first get covered lines only
    cov.start()
    old_out = sys.stdout
    old_err = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')  
    pytest.main([f"{test_file}.py", "--cache-clear"])
    sys.stdout = old_out
    sys.stderr = old_err
    cov.stop()

    out_filename = f"{test_file}_cov.json"
    cov.json_report(morfs=[target_file], outfile=out_filename)
    json_str = "".join(open(out_filename, "r").readlines())
    decoder = json.JSONDecoder()        
    coverage = decoder.decode(json_str)
    covered_lines.extend(coverage["files"][target_file]["executed_lines"])

    cov = Coverage(source=["."], omit=test_files)
    module = import_module(test_file)
    members = getmembers(module, isfunction)

    for member in members:
        test_name = member[0]
        test_names.append(test_name)
        
        cov.erase()
        cov.start()
        old_out = sys.stdout
        old_err = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        test_result = pytest.main([f"{test_file}.py::{test_name}", "--cache-clear"])
        
        sys.stdout = old_out
        sys.stderr = old_err
        cov.stop()
        
        out_filename = f"{test_name}_cov.json"
        cov.json_report(morfs=[target_file], outfile=out_filename)

        json_str = "".join(open(out_filename, "r").readlines())
        decoder = json.JSONDecoder()
        coverage = decoder.decode(json_str)
        test_results[test_name] = test_result==pytest.ExitCode.OK
        test_traces[test_name] = coverage["files"][target_file]

        # os.remove(out_filename)k

spectrum = generate_spectrum(test_traces, test_results)
scores = op2(spectrum)
print(scores)
print(ranking(scores))

    
