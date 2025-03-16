from dataclasses import dataclass
from picozk import util, config
# from picozk.binary_int import *
import math
import emp_bridge


'''
    Wires are actually holding EMP objects.
    ArithmeticWires hold IntFps - EMP arithmetic integers.
    BinaryWires hold Bits - EMP single bits.
    BinaryInts hold Integers - EMP binary integers.
'''
@dataclass(unsafe_hash=True)
class Wire:
    wire: str

@dataclass(unsafe_hash=True)
class ArithmeticWire(Wire):
    def reveal(self, expect=None, party=emp_bridge.PUBLIC, signed=True):
        # Uncomment for alternate reveal functionality. reveal_expect takes an expected integer value &
        # returns True if the wire value matches. Otherwise, EMP stops.
        # if expect:
        #    return self.wire.reveal_expect(expect)
        return self.wire.reveal_no_expect()

    def __add__(self, other):
        if type(other) == ArithmeticWire:
            emp_wire = self.wire + other.wire
            return ArithmeticWire(emp_wire)
        elif type(other == int):
            arith = ArithmeticWire(emp_bridge.EMPIntFp.from_constant(other, emp_bridge.PUBLIC))
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
        if type(other) == ArithmeticWire:
            emp_wire = self.wire * other.wire
            return ArithmeticWire(emp_wire)
        elif type(other) == int:
            if other < 0:
                raise Exception("Only positive Python integers allowed in arithmeticwire __mul__")
            emp_wire = self.wire * other
            return ArithmeticWire(emp_wire)

    # def __pow__(self, other):
    # Ask about how to implement this, given negative numbers.

    def __floordiv__(self, other):
        raise Exception('unsupported')
        # Ask about implementation - e.g. is binint division floor division?

    def __mod__(self, other):
        if type(other) == ArithmeticWire:
            mod_result = self.to_binary() % other.to_binary()
            return mod_result.to_arithmetic()
        if type(other) == int:
            bin_val = self.to_binary()
            temp = BinaryInt(emp_bridge.EMPBitInt.from_val(bin_val.wire.size(), other, emp_bridge.PUBLIC))
            mod_result = bin_val % temp
            return mod_result.to_arithmetic()

    def to_binary(self):
        converted_emp_bint = emp_bridge.intfp_to_bitint(self.wire)
        return BinaryInt(converted_emp_bint)

@dataclass(unsafe_hash=True)
class BinaryWire(Wire):
    def reveal(self, expect=None, party=emp_bridge.PUBLIC, signed=True):
        return self.wire.reveal()

    def __ne__(self, other):
        emp_wire = self.wire != other.wire
        return BinaryWire(emp_wire)

    def __eq__(self, other):
        emp_wire = self.wire == other.wire
        return BinaryWire(emp_wire)
    __req__ = __eq__

    def __and__(self, other):
        emp_wire = self.wire & other.wire
        return BinaryWire(emp_wire)

    def __or__(self, other):
        emp_wire = self.wire | other.wire
        return BinaryWire(emp_wire)

    def __invert__(self):
        inv_wire = ~self.wire
        return BinaryWire(inv_wire)

    def __xor__(self, other):
        emp_wire = self.wire ^ other.wire
        return BinaryWire(emp_wire)

@dataclass
class BinaryInt(Wire):
    def __init__(self, bits: list[BinaryWire]):
        emp_bit_list = list()
        for bit in bits:
            emp_bit_list.append(bit.wire)
        self.wire = emp_bridge.EMPBitInt.from_bits(emp_bit_list)

    def reveal(self, expect=None, party=emp_bridge.PUBLIC, signed=True):

        # Alternate reveal functionality; uncomment for option between signed and unsigned reveals.
        #    return self.wire.unsigned_reveal(party)
        return self.wire.signed_reveal(party)

    # Numeric comparisons
    def __eq__(self, other):
        if type(other) is BinaryInt:
            return BinaryWire(self.wire == other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryWire(self.wire == emp_int)

    def __ne__(self, other):
        if type(other) is BinaryInt:
            return BinaryWire(self.wire != other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryWire(self.wire != emp_int)

    def __lt__(self, other):
        if type(other) is BinaryInt:
            return BinaryWire(self.wire < other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryWire(self.wire < emp_int)

    def __gt__(self, other):
        if type(other) is BinaryInt:
            return BinaryWire(self.wire > other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryWire(self.wire > emp_int)

    def __le__(self, other):
        if type(other) is BinaryInt:
            return BinaryWire(self.wire <= other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryWire(self.wire <= emp_int)

    def __ge__(self, other):
        if type(other) is BinaryInt:
            return BinaryWire(self.wire >= other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryWire(self.wire >= emp_int)

    # Bit shifting operations
    def __rshift__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire >> other.wire)
        elif type(other) is int and other >= 0:
            return BinaryInt(self.wire >> other)

    def __lshift__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire << other.wire)
        elif type(other) is int and other >= 0:
            return BinaryInt(self.wire << other)

    # Numeric operations
    def __add__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire + other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryInt(self.wire + emp_int)
    __radd__ = __add__

    def __sub__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire - other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryInt(self.wire - emp_int)
    __rsub__ = __sub__

    def __neg__(self):
        return BinaryInt(-self.wire)

    def __mul__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire * other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryInt(self.wire * emp_int)

    def __truediv__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire / other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryInt(self.wire / emp_int)

    def __mod__(self, other):
        emp_int = self.wire % other.wire
        return BinaryInt(emp_int)

    # Bit operations
    def __xor__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire ^ other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryInt(self.wire ^ emp_int)

    def __and__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire & other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryInt(self.wire & emp_int)

    def __or__(self, other):
        if type(other) is BinaryInt:
            return BinaryInt(self.wire | other.wire)
        if type(other) is int:
            emp_int = emp_bridge.EMPBitInt.from_val(self.wire.size(), other, emp_bridge.PUBLIC)
            return BinaryInt(self.wire | emp_int)

    def __getitem__(self, item):
        bit_list = list()
        for bit in self.wire[item]:
            bit_list.append(bit)
        return bit_list

    def size(self):
        return self.wire.size()

    def abs(self):
        emp_int = self.wire.abs()
        return BinaryInt(emp_int)

    # Unsafe; ensure downsizing does not lose information!
    def resize(self, size, signed_extend=True):
        emp_int = self.wire.resize(size, signed_extend)
        return BinaryInt(emp_int)

    def leading_zeroes(self):
        emp_int = self.wire.leading_zeroes()
        return BinaryInt(emp_int)

    def hamming_weight(self):
        emp_int = self.wire.hamming_weight()
        return BinaryInt(emp_int)

    def get_index(self, index):
        emp_bit = self.wire.get_index(index)
        return BinaryWire(emp_bit)

    def rotr(self, shift):
        bw = self.wire.size()
        bit_list = self[bw - shift:] + self[:bw - shift]
        emp_int = emp_bridge.EMPBitInt.from_bits(bit_list)
        return BinaryInt(emp_int)

    def rotl(self, shift):
        bit_list = self[shift:] + self[:shift]
        emp_int = emp_bridge.EMPBitInt.from_bits(bit_list)
        return BinaryInt(emp_int)

    '''
        # Get the second least significant bit of the bint, where the negative sign is stored.
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
