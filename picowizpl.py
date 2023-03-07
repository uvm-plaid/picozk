import sys
import numpy as np
from dataclasses import dataclass
import pandas as pd
import numpy as np

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
        self.emit('@type field 2305843009213693951;')
        self.emit('@begin')

        self.witness_file.write('version 2.0.0-beta;\n')
        self.witness_file.write('private_input;\n')
        self.witness_file.write('@type field 2305843009213693951;\n')
        self.witness_file.write('@begin\n')

        ins_file = open(self.file_prefix + '.type0.ins', 'w')
        ins_file.write('version 2.0.0-beta;\n')
        ins_file.write('public_input;\n')
        ins_file.write('@type field 2305843009213693951;\n')
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

