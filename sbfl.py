from scipy.stats import rankdata
from tabulate import tabulate
from test_runner import get_test_methods, get_test_method_result, get_total_coverage
import argparse
import sys

def generate_spectrum(test_names, test_traces, covered_lines, test_results):
    """Computes spectrum from given data
    test_names -- a list of test function names
    test_traces -- a dictionary of test traces (keys are test names)
    covered_lines -- a list of line numbers that are covered at least once
    test_results -- a dictionary of test pass (True)/fail (False) results 
    """
    spectrum = []

    # ...
    
    return spectrum

def op2(spectrum):
    """Implements the Op2 risk evaluation formula"""
    scores = []

    # ...
    
    return scores

def wong1(spectrum):
    """Implements the Wong1 risk evaluation formula"""
    scores = []

    # ...
    
    return scores

def tarantula(spectrum):
    """Implements the Tarantula risk evaluation formula"""
    scores = []

    # ...
    
    return scores

def ranking(scores):
    lines = [x[0] for x in scores]
    raw_scores = [x[1] for x in scores]
    ranks = len(raw_scores) - rankdata(raw_scores, method="max").astype(int) + 1
    return list(zip(lines, ranks))


def main(target_filename, test_file):
    test_names = []
    test_results = {}
    test_traces = {}

    total_coverage = get_total_coverage(target_file, test_file)
    covered_lines = total_coverage["executed_lines"]

    test_methods = get_test_methods(test_file)
    
    for member in test_methods:
        test_name = member[0]
        test_names.append(test_name)
        result, coverage = get_test_method_result(target_file, test_file, test_name)
        test_results[test_name] = result
        test_traces[test_name] = coverage

    spectrum = generate_spectrum(test_names, test_traces, covered_lines, test_results)
    scores = wong1(spectrum)
    ranks = ranking(scores)

    rows = []
    for (score, rank) in zip(scores, ranks):
        rows.append([score[0], score[1], rank[1]])
    print(tabulate(rows, headers=["Line", "Score", "Rank"]))
    return scores, ranks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Spectrum Based Fault Localisation')
    parser.add_argument("-f", "--target_file", required=True,
                        help='the directory that contains the files to apply SBFL analysis')
    parser.add_argument('-t', "--test_file", required=True,
                        help='the  PyTest test file')

    args = parser.parse_args()
    target_file = args.target_file
    test_file = args.test_file
    
    scores, ranks = main(target_file, test_file)