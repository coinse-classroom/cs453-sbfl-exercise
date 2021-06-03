from coverage import Coverage
from inspect import getmembers, isfunction
from importlib import import_module
from scipy.stats import rankdata
from tabulate import tabulate
import pytest
import os
import glob
import argparse
import sys
import json

def generate_spectrum(test_names, test_traces, covered_lines, test_results):
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

def ranking(scores):
    lines = [x[0] for x in scores]
    raw_scores = [x[1] for x in scores]
    ranks = len(raw_scores) - rankdata(raw_scores, method="max").astype(int) + 1
    return list(zip(lines, ranks))

def get_total_coverage(target_dir, target_filename, test_files):
    cov = Coverage(source=["./examples"], omit=test_files)
    cov.erase()

    cov.start()
    old_out = sys.stdout
    old_err = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')  

    for test_file in test_files:
        test_name = os.path.basename(test_file)
        test_name = os.path.splitext(test_name)[0]        
        pytest.main([f"{test_file}", "--cache-clear"])

    sys.stdout = old_out
    sys.stderr = old_err
    cov.stop()

    out_filename = f"{test_file}_cov.json"
    cov.json_report(morfs=[target_filename], outfile=out_filename)
    json_str = "".join(open(out_filename, "r").readlines())
    decoder = json.JSONDecoder()        
    coverage = decoder.decode(json_str)
    os.remove(out_filename)
    return coverage["files"][target_filename]

def get_test_result(target_dir, target_filename, test_file, test_methodname):
    cov = Coverage(source=["./examples"], omit=[test_file])
    cov.erase()

    cov.start()
    old_out = sys.stdout
    old_err = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')  

    
    test_name = os.path.basename(test_file)
    test_name = os.path.splitext(test_name)[0]        
    
    test_result = pytest.main([f"{test_file}::{test_methodname}", "--cache-clear"])

    sys.stdout = old_out
    sys.stderr = old_err
    cov.stop()

    out_filename = f"{test_file}_cov.json"
    cov.json_report(morfs=[target_filename], outfile=out_filename)
    json_str = "".join(open(out_filename, "r").readlines())
    decoder = json.JSONDecoder()        
    coverage = decoder.decode(json_str)
    os.remove(out_filename)

    return test_result == pytest.ExitCode.OK, coverage["files"][target_filename]

def get_test_methods(pytest_file):
    test_name = os.path.splitext(pytest_file)[0]
    test_name = test_name.replace("/", ".")
    module = import_module(test_name)
    return getmembers(module, isfunction)

def main(source_dir, target_file, test_dir):

    test_files = glob.glob(os.path.join(test_dir, "test_*.py"))
    test_names = []
    test_results = {}
    test_traces = {}

    total_coverage = get_total_coverage(source_dir, target_file, test_files)
    covered_lines = total_coverage["executed_lines"]

    for test_file in test_files:
        test_methods = get_test_methods(test_file)
        
        for member in test_methods:
            test_name = member[0]
            test_names.append(test_name)
            
            result, coverage = get_test_result(source_dir, target_file, test_file, test_name)
            
            test_results[test_name] = result
            test_traces[test_name] = coverage

    spectrum = generate_spectrum(test_names, test_traces, covered_lines, test_results)
    scores = op2(spectrum)
    ranks = ranking(scores)
    return scores, ranks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Spectrum Based Fault Localisation')
    parser.add_argument("-s", "--source_dir", required=True,
                        help='the directory that contains Python source files')
    parser.add_argument("-f", "--target_file", required=True,
                        help='the file to apply SBFL analysis')
    parser.add_argument('-t', "--test_dir", required=True,
                        help='the directory that contains PyTest test files (test_*.py)')

    args = parser.parse_args()

    target_file = args.target_file
    source_dir = args.source_dir
    test_dir = args.test_dir
    
    scores, ranks = main(source_dir, target_file, test_dir)
    rows = []
    for (score, rank) in zip(scores, ranks):
        rows.append([score[0], score[1], rank[1] + 1])
    print(tabulate(rows, headers=["Line", "Score", "Rank"]))
