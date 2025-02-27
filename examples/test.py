from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    a = SecretInt(20, ARITH)
    b = SecretBit(False)
    c = SecretInt(-100, BINARY)
    print(reveal(c, signed=True, party=emp_bridge.BOB, expect=100))
