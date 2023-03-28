from dataclasses import dataclass
from typing import List
from .compiler import *
from . import config
from . import util

@dataclass
class BinaryInt:
    wires: List[any] # should be Wire, but causes a circular import

    def _wires_of(self, v):
        if isinstance(v, BinaryInt):
            return v.wires
        elif isinstance(v, int):
            return util.encode_int(v, 2**len(self.wires))
        else:
            raise Exception('no wires for value:', v)

    def __eq__(self, other):
        ok = 1
        for w1, w2 in zip(self.wires, self._wires_of(other)):
            ok = ok * ((w1 * w2) + ((w1 + 1) * (w2 + 1)))
        return ok

    def is_negative(self):
        return self.wires[0]
