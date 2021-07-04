## Spectrum Based Fault Localisation

Our aim is to re-use the test coverage collection code from TCP exercise, and implement a few SBFL risk evaluation formulas to localise the given example fault in `examples/mid.py`. The given skeleton already contains coverage collection algorithms (in `test_runner.py`).

What we want to do is the following:

1. First, execute all given test cases to identify all the covered lines.
2. Subseqently, execute each individual test case separately, and collect their coverage.
3. Convert the individual coverage and test results into program spectrum for covered lines.
4. Compute Risk Evaluation scores for each of the covered lines, using one of the following Risk Evaluation Formulas: Op2, Tarantula, Wong1
5. Print out the ranking

An example output ranking, computed with Op2, looks like the following:

```
  Line      Score    Rank
------  ---------  ------
     1   0              7
     2   0.166667       4
     3   0.166667       4
     4   0.5            3
     5  -0.166667       8
     6   0.666667       2
     7   0.833333       1
     9  -0.333333      11
    10  -0.166667       8
    11  -0.166667       8
    13   0.166667       4
```

Risk evaluation formulas are defied as follows:

- Op2: `ef - ep / (ep + np + 1)`
- Tarantula: `(ef / (ef + nf)) / (ef / (ef + nf) + ep / (ep + np))`
- Wong1: `ef`