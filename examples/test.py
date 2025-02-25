from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    x = SecretInt(6, ARITH)
    y = SecretInt(3, ARITH)
    z = SecretInt(9, ARITH)
    #result = x > y
    result2 = (x + 3) == z
    #print("x (6) > y (3)?", reveal(result))
    print("x + 3 (9) == z (9)?", reveal(result2))
