from dataclasses import dataclass
from picozk import util, config
# from picozk.binary_int import *
import math
import emp_bridge

# BooleanWire is an ArithmeticWire that is treated as a boolean.
# BinaryWire is just one bit. ~ EMPBit class.
# to_binary should convert an AW into a bint
# EMPBit is wrapped by BinaryWire.
# EMPIntFps are wrapped by ArithmeticWires (or BooleanWires, but only as a result of a comparison.
# EMPBitInts are wrapped by binary_ints.

DEF_LEN = 2**61-1

def val_of(x):
    if isinstance(x, Wire):
        if x.wire is None:
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
    # val: int
    # field: int
    # party: int

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
        self.wire = self.wire.negate()
        return self

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
        converted_emp_bint = emp_bridge.intfp_to_bitint(self.wire)
        return BinaryInt(converted_emp_bint)

@dataclass(unsafe_hash=True)
class BinaryWire(Wire):
    def __eq__(self, other): # This is essentially a xor, but adding 1 so that it is correct
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

@dataclass
class BinaryInt:
    wire: str

    def _wires_of(self, v):
        if isinstance(v, BinaryInt):
            return v.wires
        elif isinstance(v, int):
            return util.encode_int(v, 2**len(self.wires))
        else:
            raise Exception('no wires for value:', v)

    def __eq__(self, other):
        if type(other) is BinaryInt:
            emp_bit = self.wire == other.wire
            return BinaryWire(emp_bit)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(other.bit_length(), other, emp_bridge.PUBLIC)
            other_emp = BinaryInt(emp_int)
            emp_bit = self.wire == other_emp.wire
            return BinaryWire(emp_bit)

    def __add__(self, other):
        out_wires = []
        carry = 0

        for a, b in zip(reversed(self.wires), reversed(self._wires_of(other))):
            ab = a + b
            out = ab + carry % 2
            out_wires.append(out)
            carry = ((a + carry) * (b + carry) + carry) % 2
        return BinaryInt(list(reversed(out_wires)))
    __radd__ = __add__

    def __rshift__(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt([0 for _ in range(n)] + self.wires[:bw-n])

    def __lshift__(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt(self.wires[n:] + [0 for _ in range(n)])

    def rotr(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt(self.wires[bw-n:] + self.wires[:bw-n])

    def rotl(self, n):
        assert isinstance(n, int)
        bw = len(self.wires)
        return BinaryInt(self.wires[n:] + self.wires[:n])

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

    def to_arithmetic(self, field=None):
        if field is None:
            field = config.cc.fields[0]
            field_type = 0
        else:
            field_type = config.cc.fields.index(field)

        num_bits = util.get_bits_for_field(field)
        assert num_bits >= len(self.wires)

        wire_names = config.cc.allocate(num_bits, field=2)
        # pad with 0s
        wire_vals = [0]*(num_bits-len(self.wires)) + self.wires

        for new_w, old_w in zip(wire_names, wire_vals):
            if isinstance(old_w, int):
                config.cc.emit(f'  {new_w} <- {config.cc.BINARY_TYPE}: < {old_w} >;')
            elif isinstance(old_w, wire.BinaryWire):
                config.cc.emit(f'  {new_w} <- {config.cc.BINARY_TYPE}: {old_w.wire};')
            else:
                raise Exception('Unsupported wire element:', old_w)

        bits = [wire.val_of(b) for b in self.wires]
        val = util.decode_int(bits)

        r = config.cc.next_wire()

        config.cc.emit(f'  {field_type}: {r} <- @convert({config.cc.BINARY_TYPE}: {wire_names[0]} ... {wire_names[-1]});')

        return wire.ArithmeticWire(r, val, field)