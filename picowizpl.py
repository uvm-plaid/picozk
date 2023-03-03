import sys
import numpy as np
from dataclasses import dataclass
import pandas as pd
import numpy as np

relation_file = None
witness_file = None

def emit(s=''):
    global relation_file
    relation_file.write(s)
    relation_file.write('\n')

def add_to_witness(x):
    r = next_wire()
    emit(f'  {r} <- @private;')
    witness_file.write(f'  < {x} >;\n')
    return Wire(r, x)

def val_of(x):
    if isinstance(x, Wire):
        if x.val is None:
            raise Exception(f'Attempt to find value of None in object {x}')
        else:
            return x.val
    else:
        return x

def wire_of(e):
    if isinstance(e, Wire):
        return e.wire
    elif isinstance(e, int):
        r = next_wire()
        emit(f'  {r} <- <{e}>;')
        return r

current_wire = 0
def next_wire():
    global current_wire
    r = current_wire
    current_wire += 1
    return '$' + str(r)

def SecretInt(x):
    return add_to_witness(x)


@dataclass
class Wire:
    wire: str
    val: any

    def __add__(self, other):
        r = next_wire()
        emit(f'  {r} <- @add({self.wire}, {wire_of(other)});')
        return Wire(r, self.val + val_of(other))

    def __radd__(self, other):
        r = next_wire()
        emit(f'  {r} <- @add({self.wire}, {wire_of(other)});')
        return Wire(r, self.val + val_of(other))

    def __mul__(self, other):
        r = next_wire()
        emit(f'  {r} <- @mul({self.wire}, {wire_of(other)});')
        return Wire(r, self.val * val_of(other))

    def __rmul__(self, other):
        r = next_wire()
        emit(f'  {r} <- @mul({self.wire}, {wire_of(other)});')
        return Wire(r, self.val * val_of(other))


def open_picowizpl(filename):
    global witness_file
    global relation_file
    witness_file = open(filename + '.type0.wit', 'w')
    relation_file = open(filename + '.rel', 'w')

def close_picowizpl():
    global witness_file
    global relation_file
    witness_file.close()
    relation_file.close()
