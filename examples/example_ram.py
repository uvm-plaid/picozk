from picozk import *

with PicoZKCompiler('picozk_test', options=['ram']):
    x = ZKList([1, 2, 3, 4, 5])
    y = x[3]
    x[3] = 0
    assert0(y - val_of(y))
    z = x[3]
    assert0(y - val_of(y))
    assert0(z - val_of(z))
