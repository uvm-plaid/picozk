from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    y = SecretInt(6, ARITH)
    z = SecretInt(5, ARITH)
    result = z + y
    x = SecretInt(11, ARITH)
    print(reveal(x == result))
