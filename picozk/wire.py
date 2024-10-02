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
    wire: str  # wire is actually holding an EMP object, where supported
    val: int
    field: int
    party: int

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
        diff = self - other
        diff_inv_val = 0 if diff.val == 0 else util.modular_inverse(diff.val, self.field)
        res_val = 0 if diff.val == 0 else 1
        diff_inv = config.cc.add_to_witness(diff_inv_val, self.field)
        res = config.cc.add_to_witness(res_val, self.field)
        should_be_zero = (diff_inv + 1) * diff * res - (res + diff)

        assert should_be_zero.val == 0, f'Failed zero check: {should_be_zero}'
        rv = should_be_zero.wire.reveal()
        assert rv == 0, f'Failed reveal zero check: {rv}, {self.val}:{self.wire.reveal()}'

        final_res = (res * (res.field - 1)) + 1

        return BooleanWire(final_res.wire, final_res.val, final_res.field)

    __req__ = __eq__

    def is_negative(self):
        # TODO: fix this faked function
        #raise Exception('unsupported')

        if self.val <= self.field/2:
            return config.cc.add_to_witness(0, self.field)
        else:
            return config.cc.add_to_witness(1, self.field)

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
        return BinaryInt(emp_bridge.from_val(self.wire.reveal().bit_length(), self.wire.reveal(), self.party))

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
