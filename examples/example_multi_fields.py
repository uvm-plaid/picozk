from picozk import *

with PicoZKCompiler('picozk_test', field=[9, 97]):
    x = SecretInt(5, field=9)
    y = SecretInt(5, field=97)
    z = SecretBit(1)
    xc = x.to_binary().to_arithmetic(field=97)
    print(xc)
    #assert0(x - y)
    assert0(xc - y)
