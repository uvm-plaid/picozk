from dataclasses import dataclass
from typing import List
import pandas as pd
import numpy as np
import functools
from .wire import *
from .binary_int import BinaryInt
from . import config

def SecretInt(x):
    assert x % config.cc.field == x
    return config.cc.add_to_witness(int(x) % config.cc.field)

def SecretBit(x):
    assert x % 2 == x
    return config.cc.add_to_binary_witness(int(x) % 2)

def reveal(x):
    config.cc.emit_gate('assert_zero', (x + (-val_of(x))).wire, effect=True, field=x.field)

def assert0(x):
    config.cc.emit_gate('assert_zero', x.wire, effect=True, field=x.field)

def mux(a, b, c):
    if isinstance(a, int):
        return b if a else c
    elif isinstance(a, BooleanWire):
        return a.to_arith() * b + (~a).to_arith() * c
    else:
        raise Exception('unknown type for mux:', a)



@dataclass
class WireBundle:
    wires: List[Wire]


class PicoZKCompiler(object):
    def __init__(self, file_prefix, field=2**61-1, options=[]):
        self.file_prefix = file_prefix
        self.current_wire = 0
        self.field = field
        self.options = options

        self.ARITH_TYPE = 0
        self.BINARY_TYPE = 1
        self.RAM_TYPE = 2

    def emit(self, s=''):
        self.relation_file.write(s)
        self.relation_file.write('\n')

    def type_of(self, field):
        if field == self.field:
            return self.ARITH_TYPE
        elif field == 2:
            return self.BINARY_TYPE
        elif field == None:
            return self.ARITH_TYPE
        else:
            raise Exception('no known type for field:', field)

    def emit_call(self, call, *args):
        args_str = ', '.join([str(a) for a in args])
        r = self.next_wire()
        self.emit(f'  {r} <- @call({call}, {args_str});')
        return r

    def emit_gate(self, gate, *args, effect=False, field=None):
        type_arg = self.type_of(field)
        args_str = ', '.join([str(a) for a in args])
        if effect:
            self.emit(f'  @{gate}({type_arg}: {args_str});')
            return
        else:
            r = self.next_wire()
            self.emit(f'  {r} <- @{gate}({type_arg}: {args_str});')
            return r

    def allocate(self, n, field=None):
        i = self.current_wire
        self.current_wire += n
        self.emit_gate('new', f'${i} ... ${i + n-1}', effect=True, field=field)
        return [f'${i}' for i in range(i, i+n)]

    def add_to_witness(self, x):
        r = self.next_wire()
        self.emit(f'  {r} <- @private();')
        self.witness_file.write(f'  < {x} >;\n')
        return ArithmeticWire(r, x, config.cc.field)

    def add_to_binary_witness(self, x):
        r = self.next_wire()
        self.emit(f'  {r} <- @private();')
        self.witness_file.write(f'  < {x} >;\n')
        return BinaryWire(r, x, 2)

    @functools.cache
    def constant_wire(self, e):
        v = int(e) % self.field
        r = self.next_wire()
        self.emit(f'  {r} <- <{v}>;')
        return r

    def next_wire(self):
        r = self.current_wire
        self.current_wire += 1
        return '$' + str(r)

    def __enter__(self):
        global cc
        config.cc = self
        cc = self
        self.witness_file = open(self.file_prefix + '.type0.wit', 'w')
        self.relation_file = open(self.file_prefix + '.rel', 'w')

        self.emit('version 2.0.0-beta;')
        self.emit('circuit;')
        self.emit('@plugin mux_v0;')

        if 'ram' in self.options:
            self.emit(f'@plugin ram_arith_v0;')

        self.emit(f'@type field {self.field};')
        self.emit(f'@type field 2;')

        if 'ram' in self.options:
            s = '@type @plugin(ram_arith_v0, ram, 0, {0}, {1}, {2});'
            self.emit(s.format(20, # number of rams
                               2000, # total allocation size
                               2000)) # not sure

        bits_per_fe = util.get_bits_for_field(self.field)
        self.emit(f'@convert(@out: {self.ARITH_TYPE}:1, @in: {self.BINARY_TYPE}:{bits_per_fe});')
        self.emit(f'@convert(@out: {self.BINARY_TYPE}:{bits_per_fe}, @in: {self.ARITH_TYPE}:1);')

        self.emit('@begin')

        self.emit('  @function(mux, @out: 0:1, @in: 0:1, 0:1, 0:1)')
        self.emit('    @plugin(mux_v0, permissive);')

        if 'ram' in self.options:
            self.emit(f'  @function(read_ram, @out: 0:1, @in: {self.RAM_TYPE}:1, 0:1)')
            self.emit('    @plugin(ram_arith_v0, read);')
            self.emit(f'  @function(write_ram, @in: {self.RAM_TYPE}:1, 0:1, 0:1)')
            self.emit('    @plugin(ram_arith_v0, write);')
            self.emit()

        self.witness_file.write('version 2.0.0-beta;\n')
        self.witness_file.write('private_input;\n')
        self.witness_file.write(f'@type field {self.field};\n')
        self.witness_file.write('@begin\n')

        binary_wit_file = open(self.file_prefix + '.type1.wit', 'w')
        binary_wit_file.write('version 2.0.0-beta;\n')
        binary_wit_file.write('private_input;\n')
        binary_wit_file.write(f'@type field 2;\n')
        binary_wit_file.write('@begin\n')
        binary_wit_file.write('@end\n')
        binary_wit_file.close()

        ins_file = open(self.file_prefix + '.type0.ins', 'w')
        ins_file.write('version 2.0.0-beta;\n')
        ins_file.write('public_input;\n')
        ins_file.write(f'@type field {self.field};\n')
        ins_file.write('@begin\n')
        ins_file.write('@end\n')
        ins_file.close()

        binary_ins_file = open(self.file_prefix + '.type1.ins', 'w')
        binary_ins_file.write('version 2.0.0-beta;\n')
        binary_ins_file.write('public_input;\n')
        binary_ins_file.write(f'@type field 2;\n')
        binary_ins_file.write('@begin\n')
        binary_ins_file.write('@end\n')
        binary_ins_file.close()


    def __exit__(self, exception_type, exception_value, traceback):
        global cc

        self.emit('@end')
        self.witness_file.write('@end\n')

        self.relation_file.close()
        self.witness_file.close()
        cc = None
