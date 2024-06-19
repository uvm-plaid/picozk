from dataclasses import dataclass
from picozk import util, config
from picozk.binary_int import *
import math

import emp_bridge

def val_of(x):
    if isinstance(x, Wire):
        if x.val is None:
            raise Exception(f'Attempt to find value of None in object {x}')
        else:
            return x.val
    elif isinstance(x, bool):
        return int(x)
    else:
        return x

def wire_of(e):
    if isinstance(e, Wire):
        return e.wire
    elif isinstance(e, int):
        return config.cc.constant_wire(e).wire
    else:
        raise Exception('no wire for value', e, 'of type', type(e))


@dataclass(unsafe_hash=True)
class Wire:
    wire: str
    val: int
    field: int

    def __add__(self, other):
        if isinstance(other, int) and other % self.field == 0:
            return self
        else:
            if isinstance(other, Wire):
                assert other.field == self.field
                assert type(self) == type(other), f'incompatible types: {type(self)}, {type(other)}'
                r = self.wire + other.wire
            elif isinstance(other, int):
                r = self.wire + wire_of(other)
            else:
                raise Exception(f'unknown type for addition: {type(other)}')

            return type(self)(r, (self.val + val_of(other)) % self.field, self.field)
    __radd__ = __add__

    def __mul__(self, other):
        if isinstance(other, int) and other % self.field == 0:
            return 0
        else:
            if isinstance(other, Wire):
                assert other.field == self.field
                assert type(self) == type(other), f'incompatible types: {type(self)}, {type(other)}'
                r = self.wire * other.wire
            elif isinstance(other, int):
                r = self.wire * wire_of(other)
            else:
                raise Exception(f'unknown type for multiplication: {type(other)}')

            return type(self)(r, (self.val * val_of(other)) % self.field, self.field)
    __rmul__ = __mul__

    def __mod__(self, other):
        assert isinstance(other, int)
        assert other == self.field
        return self

    def __bool__(self):
        raise Exception('unsupported')

    def __int__(self):
        raise Exception('unsupported')

@dataclass(unsafe_hash=True)
class BooleanWire(Wire):
    def __and__(self, other):
        return self * other
    __rand__ = __and__

    def __or__(self, other):
        return (l * r) * (self.field - 1) + (l + r)
    __ror__ = __or__

    def __invert__(self):
        return (self * (self.field - 1)) + 1

    def __rsub__(self, other):
        assert other == 1
        return ~self

    def to_arith(self):
        return ArithmeticWire(self.wire, self.val, self.field)

    def if_else(self, then_val, else_val):
        return else_val + self.to_arith() * (then_val - else_val)

@dataclass(unsafe_hash=True)
class ArithmeticWire(Wire):
    def __neg__(self):
        return self * (self.field - 1)

    def __sub__(self, other):
        return self + (-other)
    def __rsub__(self, other):
        return (-self) + other

    def __eq__(self, other):
        raise Exception('unsupported')
    __req__ = __eq__

    def is_negative(self):
        raise Exception('unsupported')

    def __lt__(self, other):
        return (self - other).is_negative()

    def __gt__(self, other):
        return (other - self).is_negative()

    def __le__(self, other):
        return ~(self > other)

    def __ge__(self, other):
        return ~(self < other)

    def __pow__(self, other, p=None):
        def exp_by_squaring(x, n):
            assert n > 0
            if n%2 == 0:
                if n // 2 == 1:
                    return x * x
                else:
                    return exp_by_squaring(x * x,  n // 2)
            else:
                return x * exp_by_squaring(x * x, (n - 1) // 2)

        assert isinstance(other, int)
        if p != None:
            assert p == self.field
        return exp_by_squaring(self, other)

    def __floordiv__(self, other):
        raise Exception('unsupported')

    def __mod__(self, other):
        assert isinstance(other, int)
        if other == self.field:
            return self
        elif math.log2(other) == int(math.log2(other)):
            raise Exception('unsupported')
            # bits_to_keep = int(math.log2(other))
            # binary_rep = self.to_binary()
            # new_binary_rep = BinaryInt(binary_rep.wires[-bits_to_keep:])
            # return new_binary_rep.to_arithmetic()
        else:
            raise Exception('unsupported modulus:', other)

    def to_binary(self):
        raise Exception('unsupported')

@dataclass(unsafe_hash=True)
class BinaryWire(Wire):
    def __eq__(self, other):
        return (self + other) + 1
    __req__ = __eq__

    def __invert__(self):
        return self + 1

    def to_bool(self):
        assert self.field == 2
        raise Exception('unsupported')

    __xor__  = Wire.__add__
    __rxor__ = __xor__
    __and__  = Wire.__mul__
    __rand__ = __and__

    def __invert__(self):
        return self + 1
