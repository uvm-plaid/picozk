from picozk import *

with PicoZKCompiler('picozk_test'):
    x = SecretInt(5)
    z = x + x * x
    assert0(z + -30)