from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    x = SecretBit(0)
    print(reveal(x))
