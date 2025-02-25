from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    y = SecretInt(-6, ARITH)
    print("Is y negative", reveal(y.is_negative()))
