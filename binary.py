from picowizpl import *
from typing import List
import galois

gf_2 = galois.GF(2)
BITWIDTH = 32

@dataclass
class BinaryInt:
    wires: List[Wire]

    def to_int(self):
        val_list = [int(val_of(x)) for x in self.wires]
        return int("".join(str(x) for x in reversed(val_list)), 2)

    def __add__(self, other):
        out_wires = []
        carry = 0

        for a, b in zip(self.wires, other.wires):
            ab = a + b
            out_wires.append(ab + carry)
            carry = (a * b) + (ab * carry)

        return BinaryInt(out_wires)

    __radd__ = __add__

def encode_int(i):
    bit_format = f'{{0:0{BITWIDTH}b}}'
    return gf_2([int(b) for b in reversed(bit_format.format(i))])

def binary_int(i):
    wires = [SecretInt(b) for b in encode_int(i)]
    return BinaryInt(wires)

def check_equal(c, i):
    for w, b in zip(c.wires, encode_int(i)):
        assert0(w + b)

with PicoWizPLCompiler('miniwizpl_test', field=2):
    v = binary_int(10)
    tot = v
    for i in range(2000):
        tot = tot + v
    #print(tot)
    print(tot.to_int())
    check_equal(tot, tot.to_int())
