from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    y = SecretInt(-100002, ARITH)
    yb = y.to_binary()
    print(type(y.wire))
    neg = yb.is_negative()
    print(yb.wire.size())
    print(reveal(neg))
