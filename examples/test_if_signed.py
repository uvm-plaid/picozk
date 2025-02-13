from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    y = SecretInt(100003, BINARY)
    print(type(y.wire))
    neg = y.is_negative()
    print(reveal(neg))
