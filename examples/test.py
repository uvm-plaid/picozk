from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    a = SecretBitInt(-100000000040400)
    neg = a.get_index(a.size() - 1)

    print(reveal(neg))