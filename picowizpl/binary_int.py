from dataclasses import dataclass
from typing import List
from .compiler import *
from . import config
from . import util

@dataclass
class BinaryInt:
    wires: List[any] # should be Wire, but causes a circular import

    def __eq__(self, other):
        other_wires = other.wires if isinstance(other, BinaryInt) else util.encode_int(other, 2**len(self.wires))

        ok = 1
        for w1, w2 in zip(self.wires, other_wires):
            ok = ok * ((w1 * w2) + ((w1 + 1) * (w2 + 1)))
        return ok


    def __le__(self, other):
        print(self, other)
        1/0

