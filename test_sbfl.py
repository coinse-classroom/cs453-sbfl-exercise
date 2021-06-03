import sbfl
from numpy.testing import assert_allclose

def test_score():
    scores, ranks = sbfl.main("examples/", "examples/mid.py", "examples/")
    assert scores[0][1] == 0
    assert_allclose(scores[1][1], float(1 / 6))

def test_rank():
    scores, ranks = sbfl.main("examples/", "examples/mid.py", "examples/")
    rank_result = {}
    for line, rank in ranks:
        rank_result[line] = rank

    assert rank_result[2] == 4
    assert rank_result[7] == 1