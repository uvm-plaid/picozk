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

@dataclass
class Wire:
    wire: str
    val: any

    def __add__(self, other):
        r = cc.next_wire()
        cc.emit(f'  {r} <- @add({self.wire}, {cc.wire_of(other)});')
        return Wire(r, self.val + val_of(other))

    def __radd__(self, other):
        r = cc.next_wire()
        cc.emit(f'  {r} <- @add({self.wire}, {cc.wire_of(other)});')
        return Wire(r, self.val + val_of(other))

    def __mul__(self, other):
        r = cc.next_wire()
        cc.emit(f'  {r} <- @mul({self.wire}, {cc.wire_of(other)});')
        return Wire(r, self.val * val_of(other))

    def __rmul__(self, other):
        r = cc.next_wire()
        cc.emit(f'  {r} <- @mul({self.wire}, {cc.wire_of(other)});')
        return Wire(r, self.val * val_of(other))


class PicoWizPLCompiler(object):
    def __init__(self, file_prefix):
        self.file_prefix = file_prefix
        self.current_wire = 0

    def emit(self, s=''):
        self.relation_file.write(s)
        self.relation_file.write('\n')

    def add_to_witness(self, x):
        r = self.next_wire()
        self.emit(f'  {r} <- @private;')
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
        self.relation_file = open(self.file_prefix + '.type0.wit', 'w')
        self.witness_file = open(self.file_prefix + '.rel', 'w')

    def __exit__(self, exception_type, exception_value, traceback):
        global cc
        self.relation_file.close()
        self.witness_file.close()
        cc = None

