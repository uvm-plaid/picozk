from picozk import *
from picozk.sha256 import ZKSHA256

with PicoZKCompiler('picozk_test', field=97):
    bit_list = [SecretBit(1), SecretBit(0), SecretBit(1)]
    x = BinaryInt.from_bits(bit_list)
    bit_list2 = [BinaryWire.from_val(1), BinaryWire.from_val(0), BinaryWire.from_val(1)]
    y = BinaryInt.from_bits(bit_list2)
    z = x ^ y
    reveal(z)
