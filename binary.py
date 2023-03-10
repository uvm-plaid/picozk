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
        return int("".join(str(x) for x in val_list), 2)

    def __add__(self, other):
        out_wires = []
        a = self.wires
        b = other.wires

        out_wires.append(a[0] + b[0])
        carry = a[0] * b[0]
        for i in range(1, len(a)-1):
            ab = a[i] + b[i]
            out_wires.append(ab + carry)
            carry = a[i] * b[i] + carry * ab
        out_wires.append(a[len(a)-1] + b[len(b)-1] + carry)

        return BinaryInt(out_wires)
    __radd__ = __add__

def binary_int(i):
    bit_format = f'{{0:0{BITWIDTH}b}}'
    bits = [int(b) for b in bit_format.format(i)]
    wires = [SecretInt(gf_2(b)) for b in bits]
    return BinaryInt(wires)

with PicoWizPLCompiler('miniwizpl_test'):
    tot = binary_int(10)
    for i in range(100):
        tot = tot + binary_int(10)
    print(tot)
    print(tot.to_int())
