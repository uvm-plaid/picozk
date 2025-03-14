from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    x = SecretBitInt(100)
    y = x.rotr(5)
    print(reveal(y))