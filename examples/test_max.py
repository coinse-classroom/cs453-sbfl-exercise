import max

def test_max1():
    assert max.print_max(3, 1) == 3

def test_max2():
    assert max.print_max(5, -4) == 5

def test_max3():
    assert max.print_max(0, -4) == 0

def test_max4():
    assert max.print_max(0, 7) == 7

def test_max5():
    assert max.print_max(-1, 3) == 3
