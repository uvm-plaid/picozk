from dataclasses import dataclass
from typing import List
from .compiler import *
from . import config
from . import util
from . import wire

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

    def __add__(self, other):
        out_wires = []
        carry = 0

        for a, b in zip(reversed(self.wires), reversed(self._wires_of(other))):
            ab = a + b
            out = ab + carry % 2
            out_wires.append(out)
            carry = (a * b) + (ab * carry) % 2
        return BinaryInt(list(reversed(out_wires)))
    __radd__ = __add__

    def __rshift__(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt([0 for _ in range(n)] + self.wires[:bw-n])

    def __lshift__(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt(self.wires[bw-n:] + [0 for _ in range(n)])

    def rotr(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt(self.wires[bw-n:] + self.wires[:bw-n])

    def rotl(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt(self.wires[:bw-n] + self.wires[bw-n:])

    def __xor__(self, other):
        out_wires = [a ^ b for a, b in zip(self.wires, self._wires_of(other))]
        return BinaryInt(out_wires)

    def __and__(self, other):
        out_wires = [a & b for a, b in zip(self.wires, self._wires_of(other))]
        return BinaryInt(out_wires)

    def __invert__(self):
        return BinaryInt([~b for b in self.wires])

    def is_negative(self):
        return self.wires[0]

    def to_arithmetic(self):
        field = config.cc.field
        wire_names = config.cc.allocate(len(self.wires), field=2)

        for new_w, old_w in zip(wire_names, self.wires):
            if isinstance(old_w, int):
                config.cc.emit(f'  {new_w} <- {config.cc.BINARY_TYPE}: < {old_w} >;')
            elif isinstance(old_w, wire.BinaryWire):
                config.cc.emit(f'  {new_w} <- {config.cc.BINARY_TYPE}: {old_w.wire};')
            else:
                raise Exception('Unsupported wire element:', old_w)

        bits = [wire.val_of(b) for b in self.wires]
        val = util.decode_int(bits)

        r = config.cc.next_wire()

        config.cc.emit(f'  {config.cc.ARITH_TYPE}: {r} <- @convert({config.cc.BINARY_TYPE}: {wire_names[0]} ... {wire_names[-1]});')

        return wire.ArithmeticWire(r, val, field)
