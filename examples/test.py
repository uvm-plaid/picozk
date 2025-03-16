from picozk import *

_h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

print(util.encode_int(x, 2**32) for x in _h)

with PicoZKCompiler('picozk_test', field=97):
    bit_list = [SecretBit(1), SecretBit(0), SecretBit(1)]

    x = BinaryInt(bit_list)
    print(reveal(x))
