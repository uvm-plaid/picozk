from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    bit_list = [SecretBit(1), SecretBit(0), SecretBit(1)]
    int_list = [1, 0, 1]

    x = BinaryInt.from_bits(bit_list).rotr(5)
    y = BinaryInt.from_bits(int_list).rotr(5)
    print(x.wire.size())
    print(reveal(x), reveal(y))
