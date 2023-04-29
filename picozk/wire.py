from dataclasses import dataclass
from . import util
from . import config
from .binary_int import *

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
        return config.cc.constant_wire(e)
    else:
        raise Exception('no wire for value', e, 'of type', type(e))


@dataclass(frozen=True)
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
                r = config.cc.emit_gate('add', self.wire, other.wire,
                                        field=self.field)
            elif isinstance(other, int):
                r = config.cc.emit_gate('addc', self.wire, f'< {other % self.field} >',
                                        field=self.field)
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
                r = config.cc.emit_gate('mul', self.wire, other.wire,
                                        field=self.field)
            elif isinstance(other, int):
                r = config.cc.emit_gate('mulc', self.wire, f'< {other % self.field} >',
                                        field=self.field)
            else:
                raise Exception(f'unknown type for multiplication: {type(other)}')

            return type(self)(r, (self.val * val_of(other)) % self.field, self.field)
    __rmul__ = __mul__

    def __mod__(self, other):
        assert isinstance(other, int)
        if other != self.field:
            raise Exception('unsupported modulus:', other)
        return self

    def __bool__(self):
        raise Exception('unsupported')

    def __int__(self):
        raise Exception('unsupported')

@dataclass(frozen=True)
class BooleanWire(Wire):
    def __and__(self, other):
        return self * other
    __rand__ = __and__

    def __or__(self, other):
        return (self * other) + (self * (~other)) + ((~self) * other)
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


@dataclass(frozen=True)
class ArithmeticWire(Wire):
    def __neg__(self):
        return self * (self.field - 1)

    def __sub__(self, other):
        return self + (-other)
    def __rsub__(self, other):
        return (-self) + other

    def __eq__(self, other):
        diff = self - other
        r = config.cc.emit_call('mux', wire_of(diff), wire_of(1), wire_of(0))
        return BooleanWire(r, int(val_of(self) == val_of(other)), self.field)
    __req__ = __eq__

    def is_negative(self):
        return self.to_binary().is_negative().to_bool()

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

    def to_binary(self):
        assert self.field > 2
        field_type = config.cc.fields.index(self.field)
        bits = util.encode_int(self.val, self.field)
        intv = util.decode_int(bits)
        wire_names = config.cc.allocate(len(bits))
        config.cc.emit(f'  {config.cc.BINARY_TYPE}: {wire_names[0]} ... {wire_names[-1]} <- @convert({field_type}: {self.wire});')
        wires = [BinaryWire(name, val, 2) for name, val in zip(wire_names, bits)]
        return BinaryInt(wires)

@dataclass(frozen=True)
class BinaryWire(Wire):
    def __eq__(self, other):
        return (self + other) + 1
    __req__ = __eq__

    def __invert__(self):
        return self + 1

    def to_bool(self):
        assert self.field == 2
        field = config.cc.fields[0]
        field_type = 0
        num_bits = util.get_bits_for_field(field)
        wire_names = config.cc.allocate(num_bits, field=2)

        for wire_name in wire_names[:-1]: # skip the last wire
            config.cc.emit(f'  {wire_name} <- {config.cc.BINARY_TYPE}: < 0 >;')

        config.cc.emit(f'  {wire_names[-1]} <- {config.cc.BINARY_TYPE}: {self.wire};')

        r = config.cc.next_wire()

        config.cc.emit(f'  {field_type}: {r} <- @convert({config.cc.BINARY_TYPE}: {wire_names[0]} ... {wire_names[-1]});')

        return BooleanWire(r, self.val, field)

    __xor__  = Wire.__add__
    __rxor__ = __xor__
    __and__  = Wire.__mul__
    __rand__ = __and__

    def __invert__(self):
        return self + 1
