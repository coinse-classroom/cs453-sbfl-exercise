def print_max(x, y):
    m = -x # fault
    if m < y:
        m = y
        if x * y < 0:
            print("different sign")
    print(m)
    return m