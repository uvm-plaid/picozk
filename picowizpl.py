from numba import jit, config
config.DISABLE_JIT = True

from dataclasses import dataclass
import pandas as pd
import numpy as np
import galois
import functools
from typing import List

# Current compiler
cc = None



def SecretInt(x):
    return cc.add_to_witness(x)

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

def allocate(n):
    i = cc.current_wire
    cc.emit(f'  @new(${i} ... ${i + n-1});')

def assert0(x):
    cc.emit(f'  @assert_zero({cc.wire_of(x)});')

def mux(a, b, c):
    if isinstance(a, int):
        return b if a else c
    else:
        return a * b + (~a) * c

@dataclass
class Wire:
    wire: str
    val: any

    def as_gf(self, gf):
        return Wire(self.wire, gf(self.val))

    def __and__(self, other):
        return self * other
    __rand__ = __and__

    def __or__(self, other):
        return (self * other) + (self * (~other)) + ((~self) * other)
    __ror__ = __or__

    def __neg__(self):
        r = cc.next_wire()
        cc.emit(f'  {r} <- @mulc({self.wire}, < {cc.field - 1} >);')
        return Wire(r, -self.val)

    def __invert__(self):
        return (-self) + 1

    def __add__(self, other):
        if isinstance(other, Wire):
            r = cc.next_wire()
            cc.emit(f'  {r} <- @add({self.wire}, {cc.wire_of(other)});')
            return Wire(r, self.val + val_of(other))
        elif isinstance(other, int):
            if other == 0:
                return self
            else:
                r = cc.next_wire()
                cc.emit(f'  {r} <- @addc({self.wire}, <{other%cc.field}>);')
                return Wire(r, self.val + other)
    __radd__ = __add__

    def __sub__(self, other):
        nother = - other
        return self + nother
    __rsub__ = __sub__

    def __mul__(self, other):
        #print('mul', self, other)
        if isinstance(other, Wire):
            r = cc.next_wire()
            cc.emit(f'  {r} <- @mul({self.wire}, {cc.wire_of(other)});')
            return Wire(r, self.val * val_of(other))
        elif isinstance(other, int):
            if other == 0:
                return 0
            else:
                r = cc.next_wire()
                cc.emit(f'  {r} <- @mulc({self.wire}, <{other%cc.field}>);')
                return Wire(r, self.val * int(other))
    __rmul__ = __mul__

    def __eq__(self, other):
        diff = self - other
        r = cc.next_wire()
        cc.emit(f'  {r} <- @call(mux, {cc.wire_of(diff)}, {cc.wire_of(1)}, {cc.wire_of(0)});')
        return Wire(r, int(val_of(self) == val_of(other)))
    __req__ = __eq__


    def __pow__(self, other):
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
        return exp_by_squaring(self, other)

@dataclass
class WireBundle:
    wires: List[Wire]

class PicoWizPLCompiler(object):
    def __init__(self, file_prefix, field=2**61-1):
        self.file_prefix = file_prefix
        self.current_wire = 0
        self.field = field

    def emit(self, s=''):
        self.relation_file.write(s)
        self.relation_file.write('\n')

    def add_to_witness(self, x):
        r = self.next_wire()
        self.emit(f'  {r} <- @private();')
        self.witness_file.write(f'  < {x} >;\n')
        return Wire(r, x)

    @functools.cache
    def constant_wire(self, e):
        v = int(e) % self.field
        r = self.next_wire()
        self.emit(f'  {r} <- <{v}>;')
        return r

    def wire_of(self, e):
        if isinstance(e, Wire):
            return e.wire
        elif isinstance(e, (int, galois.Array)):
            return self.constant_wire(e)
        else:
            raise Exception('no wire for value', e, 'of type', type(e))

    def next_wire(self):
        r = self.current_wire
        self.current_wire += 1
        return '$' + str(r)

    def __enter__(self):
        global cc
        cc = self
        self.witness_file = open(self.file_prefix + '.type0.wit', 'w')
        self.relation_file = open(self.file_prefix + '.rel', 'w')

        self.emit('version 2.0.0-beta;')
        self.emit('circuit;')
        self.emit('@plugin mux_v0;')
        self.emit(f'@type field {self.field};')
        self.emit('@begin')

        self.emit('  @function(mux, @out: 0:1, @in: 0:1, 0:1, 0:1)')
        self.emit('    @plugin(mux_v0, permissive);')


        self.witness_file.write('version 2.0.0-beta;\n')
        self.witness_file.write('private_input;\n')
        self.witness_file.write(f'@type field {self.field};\n')
        self.witness_file.write('@begin\n')

        ins_file = open(self.file_prefix + '.type0.ins', 'w')
        ins_file.write('version 2.0.0-beta;\n')
        ins_file.write('public_input;\n')
        ins_file.write(f'@type field {self.field};\n')
        ins_file.write('@begin\n')
        ins_file.write('@end\n')
        ins_file.close()


    def __exit__(self, exception_type, exception_value, traceback):
        global cc

        self.emit('@end')
        self.witness_file.write('@end\n')

        self.relation_file.close()
        self.witness_file.close()
        cc = None

