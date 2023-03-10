from numba import jit, config
config.DISABLE_JIT = True

from picowizpl import *
from typing import List
import galois
from functions import picowizpl_function
from typing import List

gf_2 = galois.GF(2)
BITWIDTH = 32

def abs_add(wires, a, b):
    return BinaryInt(wires, a.val + b.val)

@dataclass
class BinaryInt:
    wires: List[str]
    val: int

    @classmethod
    def abs(cls, bundle):
        raise Exception('might be wrong')
        bits = [int(w.val) for w in bundle.wires]
        int_val = int("".join(str(x) for x in reversed(val_list)), 2)
        wires = [w.wire for w in bundle.wires]
        return BinaryInt(wires, int_val)

    def conc(self):
        bits = encode_int(self.val)
        wires = [Wire(w, v) for w, v in zip(self.wires, bits)]
        return WireBundle(wires)

    def to_int(self):
        return self.val

    @picowizpl_function(in_wires=BITWIDTH, out_wires=BITWIDTH,
                        concfn=lambda x: x.conc(), absfn=lambda x: BinaryInt.abs(x),
                        op=abs_add)
    def __add__(self, other):
        out_wires = []
        carry = 0

        for a, b in zip(self.wires, other.wires):
            ab = a + b
            out_wires.append(ab + carry)
            carry = (a * b) + (ab * carry)

        return WireBundle(out_wires)

    __radd__ = __add__

def encode_int(i):
    bit_format = f'{{0:0{BITWIDTH}b}}'
    return gf_2([int(b) for b in reversed(bit_format.format(i))])

def binary_int(i):
    bits = encode_int(i)
    allocate(len(bits))
    wires = [SecretInt(b) for b in encode_int(i)]
    wire_names = [w.wire for w in wires]
    return BinaryInt(wire_names, i)

def check_equal(c, i):
    for w, b in zip(c.conc().wires, encode_int(i)):
        assert0(w + b)

with PicoWizPLCompiler('miniwizpl_test', field=2):
    v = binary_int(10)
    tot = v
    for i in range(2000):
        tot = tot + v

    print(tot.to_int())
    check_equal(tot, tot.to_int())
