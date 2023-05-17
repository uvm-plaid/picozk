from picozk import *

with PicoZKCompiler('picozk_test', field=[97]):
    x = SecretInt(63)
    print(f'x is: {x}')
    for i in [2,3,4,5,6]:
        y = x % (2**i)
        print(f'x % 2^{i} ({2**i}) = {y}')
        reveal(y)

