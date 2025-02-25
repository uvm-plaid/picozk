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

''' Use an EMP implementation of ArithInt comparisons. Convert result to binary & run is_negative.
Write a Python method to get the 0th bit. See if EMP implementation of bint is signed or not...
Size method in EMP can be used for comparison between bints and normal ints.'''

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

@dataclass(unsafe_hash=True)
class ArithmeticWire(Wire):
    def __add__(self, other):
        if type(other) == ArithmeticWire:
            emp_wire = self.wire + other.wire
            return ArithmeticWire(emp_wire)
        elif type(other) == BinaryInt:
            arith = other.to_arithmetic()
            return self + arith
        elif type(other == int):
            arith = ArithmeticWire(emp_bridge.EMPIntFp.from_val(other, emp_bridge.PUBLIC))
            return self + arith

    def __neg__(self):
        neg_wire = self.wire.negate()
        return ArithmeticWire(neg_wire)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __eq__(self, other):
        diff = (self - other).to_binary()
        zero = BinaryInt(emp_bridge.EMPBitInt.from_val(diff.wire.size(), 0, emp_bridge.PUBLIC))
        return diff == zero

    __req__ = __eq__

    def is_negative(self):
        temp = self.to_binary()
        return temp.is_negative()

    def __lt__(self, other):
        temp = (self - other).to_binary()
        return temp.is_negative()

    def __gt__(self, other):
        temp = (other - self).to_binary()
        return temp.is_negative()

    def __le__(self, other):
        return ~(self > other)

    def __ge__(self, other):
        return ~(self < other)

    def __mul__(self, other):


    def __pow__(self, other):
        i = 0 ''' TO IMPLEMENT '''

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
        inv_wire = ~self.wire
        return BinaryWire(inv_wire)

    def to_bool(self):
        assert self.field == 2
        raise Exception('unsupported')

    __xor__  = Wire.__add__
    __rxor__ = __xor__
    __and__  = Wire.__mul__
    __rand__ = __and__

@dataclass
class BinaryInt:
    wire: str  #

    def _wires_of(self, v):
        if isinstance(v, BinaryInt):
            return v.wires
        elif isinstance(v, int):
            return util.encode_int(v, 2**len(self.wires))
        else:
            raise Exception('no wires for value:', v)

    ''' Numeric operators '''
    def __eq__(self, other):
        if type(other) is BinaryInt:
            emp_bit = self.wire == other.wire
            return BinaryWire(emp_bit)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            other_emp = BinaryInt(emp_int)
            emp_bit = self.wire == other_emp.wire
            return BinaryWire(emp_bit)
    def __lt__(self, other):
        if type(other) is BinaryInt:
            emp_bit = self.wire < other.wire
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

    '''
        # Get the second least significant bit of the bint, where the negative sign is stored
        # Due to jank in EMP itself, negativity is stored in the lowest bit for native binary integers,
        # and in the second lowest bit for converted arith->binary integers; this function is only needed
        # for the latter. 
    '''
    def is_negative(self):
        emp_bit = self.wire.get_index(self.wire.size() - 2)
        return BinaryWire(emp_bit)

    def to_arithmetic(self):
        arith_wire = emp_bridge.bitint_to_intfp(self.wire)
        return ArithmeticWire(arith_wire)
