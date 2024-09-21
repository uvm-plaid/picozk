# distutils: language = c++

cimport EMPBridge
from EMPBridge cimport Bit
from EMPBridge cimport IntFp
from libcpp cimport bool
import sys

def setup_bool_zk(int party):
    EMPBridge.emp_setup_bool_zk(party)

def finish_bool_zk():
    EMPBridge.emp_finish_bool_zk()

def setup_arith_zk(int party):
    EMPBridge.emp_setup_arith_zk(party)

def finish_arith_zk():
    EMPBridge.emp_finish_arith_zk()

PUBLIC = 0
ALICE = 1   # PROVER
BOB = 2     # VERIFIER

cdef class EMPBit:
    cdef Bit the_bit

    @staticmethod
    def from_constant(bool val, int party):
        p = EMPBit()
        p.the_bit = Bit(val, party)
        return p

    @staticmethod
    cdef create(Bit the_bit):
        p = EMPBit()
        p.the_bit = the_bit
        return p

    def __and__(self, EMPBit other):
        cdef Bit result_bit = (self.the_bit) & (other.the_bit)
        return EMPBit.create(result_bit)

    def reveal(self):
        return self.the_bit.reveal()

cdef class EMPIntFp:
    cdef IntFp the_intfp

    # Create a new IntFp from a constant value and a party
    @staticmethod
    def from_constant(unsigned long long val, int party):
        p = EMPIntFp()
        p.the_intfp = IntFp(val, party)
        return p

    # Create a new IntFp from an existing IntFp (pointer constructor)
    @staticmethod
    cdef create(IntFp the_intfp):
        p = EMPIntFp()
        p.the_intfp = the_intfp
        return p

    def reveal(self):
        return self.the_intfp.reveal()

    def bool_reveal(self, unsigned long long val):
        return self.the_intfp.reveal(val)

    def negate(self):
        p = EMPIntFp()
        p.the_intfp = self.the_intfp.negate()
        return p

    def __add__(self, EMPIntFp other):
        cdef IntFp result_intfp = (self.the_intfp) + (other.the_intfp)
        return EMPIntFp.create(result_intfp)

    def __mul__(self, EMPIntFp other):
        cdef IntFp result_intfp = (self.the_intfp) * (other.the_intfp)
        return EMPIntFp.create(result_intfp)

def test_main(int party, int iterations):
    print('Running boolean zk...')
    setup_bool_zk(party)

    b1 = EMPBit.from_constant(True, 0)
    b2 = EMPBit.from_constant(False, 0)

    for _ in range(iterations):
        b3 = b1 & b2

    print(b3)
    print(b3.reveal())

    finish_bool_zk()
    print('Done running boolean zk')

    print('Running arithmetic zk...')
    setup_arith_zk(party)

    a1 = EMPIntFp.from_constant(5, ALICE)
    a2 = EMPIntFp.from_constant(6, ALICE)

    for _ in range(iterations):
        a3 = a1 + a2

    print(a3)
    print(a3.reveal())

    finish_arith_zk()
    print('Done running arithmetic zk')
