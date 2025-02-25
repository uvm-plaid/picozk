from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    x = SecretInt(6, ARITH)
    y = SecretInt(4, ARITH)
    z = SecretInt(0, ARITH)
    #result = x > y
    result2 = (x % 4) == z
    #print("x (6) > y (3)?", reveal(result))
    print("x (6) % 3 == z (0)?", reveal(result2))
