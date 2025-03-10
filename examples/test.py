from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    a = SecretInt(10, BINARY)
    b = SecretInt(5, BINARY)
    c = 8

    print("a > b? (Expected True, Result: ", reveal(a > b), ")")
    print("a > c? (Expected True, Result: ", reveal(a > c), ")")
    print("a < b? (Expected False, Result: ", reveal(a < b), ")")
    print("a < c? (Expected False, Result: ", reveal(a < c), ")")