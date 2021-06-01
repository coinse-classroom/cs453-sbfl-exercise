import mid

def test_mid1():
    assert 3 == mid.mid(3, 3, 5)

def test_mid2():
    assert 2 == mid.mid(1, 2, 3)

def test_mid3():
    assert 2 == mid.mid(3, 2, 1)

def test_mid4():
    assert 5 == mid.mid(5, 5, 5)

def test_mid5():
    assert 4 == mid.mid(5, 3, 4)

def test_mid6():
    assert 2 == mid.mid(2, 1, 3)