import sys
import numpy as np
from dataclasses import dataclass
import pandas as pd
import numpy as np
import galois

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
    else:
        return x

def assert0(x):
    cc.emit(f'  @assert_zero({x.wire});')

@dataclass
class Wire:
    wire: str
    val: any

    def as_gf(self, gf):
        return Wire(self.wire, gf(self.val))

    def __add__(self, other):
        r = cc.next_wire()
        cc.emit(f'  {r} <- @add({self.wire}, {cc.wire_of(other)});')
        return Wire(r, self.val + val_of(other))
    __radd__ = __add__

    def __sub__(self, other):
        n = cc.next_wire()
        r = cc.next_wire()
        cc.emit(f'  {n} <- @mulc({cc.wire_of(other)}, < {cc.field - 1} >);')
        cc.emit(f'  {r} <- @add({self.wire}, {n});')
        return Wire(r, self.val - val_of(other))
    __rsub__ = __sub__

    def __mul__(self, other):
        r = cc.next_wire()
        cc.emit(f'  {r} <- @mul({self.wire}, {cc.wire_of(other)});')
        return Wire(r, self.val * val_of(other))
    __rmul__ = __mul__

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

    def wire_of(self, e):
        if isinstance(e, Wire):
            return e.wire
        elif isinstance(e, int):
            r = self.next_wire()
            self.emit(f'  {r} <- <{e}>;')
            return r
        elif isinstance(e, galois.Array):
            r = self.next_wire()
            self.emit(f'  {r} <- <{int(e)}>;')
            return r
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
        self.emit(f'@type field {self.field};')
        self.emit('@begin')

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

