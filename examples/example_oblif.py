from picozk import *
from oblif.decorator import oblif

@oblif
def test(x):
    if x == 3:
        return x + 1
    else:
        return x + 5

with PicoZKCompiler('picozk_test'):
    x = SecretInt(5)
    r1 = test(x)
    reveal(r1)
    print(r1)

    y = SecretInt(3)
    r2 = test(y)
    reveal(r2)
    print(r2)
