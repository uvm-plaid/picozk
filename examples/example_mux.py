from picozk import *

with PicoZKCompiler('picozk_test'):
    a = SecretInt(5)
    b = SecretInt(6)
    assert0(~(a == a))
    assert0(a == b)
    assert0(mux(a == b, 30, 0))
