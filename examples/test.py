from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    bit_list = [SecretBit(1), SecretBit(0), SecretBit(1)]

    x = BinaryInt(bit_list)
    print(reveal(x))
