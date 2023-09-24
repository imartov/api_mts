def test(var):
    var += 1
    print(bool(var.__class__ == type(1)))


h = test(2)