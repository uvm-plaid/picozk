from picozk import *
from oblif.decorator import oblif

@oblif
def test(x):
    if x == 3:
        return x + 1
    else:
        return x + 5

@oblif
def test2(x):
    if x == 1:
        z = 3
    elif x == 2:
        z = 4
    elif x == 5:
        z = 6
    else:
        z = 20
    return z + 32

with PicoZKCompiler('picozk_test'):
    x = SecretInt(5)
    r1 = test(x)
    reveal(r1)
    print(r1)

    y = SecretInt(3)
    r2 = test(y)
    reveal(r2)
    print(r2)

    r3 = test2(x)
    reveal(r3)
    print(r3)
