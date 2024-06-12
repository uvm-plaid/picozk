from dataclasses import dataclass
from typing import List
import functools
from picozk.wire import *
from picozk.binary_int import BinaryInt
from picozk import config

import emp_bridge

def SecretInt(x, field=None):
    f = 2**61-1
    emp_val = emp_bridge.EMPIntFp.from_constant(x%f, emp_bridge.ALICE)
    return ArithmeticWire(emp_val, x%f, f)

def SecretBit(x):
    return config.cc.add_to_witness(x, 2)

def PublicInt(x, field=None):
    return config.cc.add_to_instance(x, field)

def PublicBit(x):
    return config.cc.add_to_instance(x, 2)

def reveal(x):
    rv = x.wire.reveal()
    assert val_of(x) == rv

def assert0(x):
    if val_of(x):
        raise Exception('Failed assert0!', x)

    rv = x.wire.reveal()
    assert rv == 0

def assert_eq(x, y):
    assert x.field == y.field
    if val_of(x) != val_of(y):
        print("x != y", x, y)

    config.cc.emit_gate('assert_zero', (x - y).wire, effect=True, field=x.field)

def mux(a, b, c):
    if isinstance(a, int):
        return b if a else c
    elif isinstance(a, BooleanWire) and \
         isinstance(b, (int, ArithmeticWire)) and \
         isinstance(c, (int, ArithmeticWire)):
        return a.if_else(b, c)
    else:
        raise Exception('unknown types for mux:', a, b, c)

def mux_bool(a, b, c):
    if isinstance(a, int):
        return b if a else c
    elif isinstance(a, BooleanWire):
        return a * b + (~a) * c
    else:
        raise Exception('unknown types for mux_bool:', a, b, c)

def modular_inverse(x, p):
    if isinstance(x, int):
        return util.modular_inverse(x, p)
    elif isinstance(x, ArithmeticWire):
        assert x.field == p
        inv = SecretInt(util.modular_inverse(val_of(x), p), field=p)
        assert0(x * inv - 1)
        return inv
    else:
        raise Exception('unknown type for modular inverse:', x)


class PicoZKCompiler(object):
    def __init__(self, party, field=2**61-1, options=[]):
        self.current_wire = 0
        self.options = options
        self.party = party

        if isinstance(field, int):
            self.fields = [field]
        elif isinstance(field, list):
            self.fields = field
        else:
            raise Exception('unknown field spec:', field)

        self.fields.append(2)                   # add the binary field
        self.BINARY_TYPE = len(self.fields) - 1 # binary type is the last field
        self.RAM_TYPE = len(self.fields)        # RAM type is the one after that

        self.no_convert_is_neg = False

    def type_of(self, field):
        if field in self.fields:
            return self.fields[field]
        elif field == 2:
            return self.BINARY_TYPE
        else:
            raise Exception('no known type for field:', field)


    def add_to_witness(self, x, field):
        if field == None:
            field_type = 0
            field = self.fields[field_type]
        else:
            field_type = self.fields.index(field)

        x = int(x)
        assert x % field == x

        r = self.next_wire()
        self.emit(f'  {r} <- @private({field_type});')
        self.witness_files[field_type].write(f'  < {x} >;\n')

        if field == 2:
            return BinaryWire(r, x, 2)
        else:
            return ArithmeticWire(r, x, field)

    def add_to_instance(self, x, field):
        if field == None:
            field_type = 0
            field = self.fields[field_type]
        else:
            field_type = self.fields.index(field)

        x = int(x)
        assert x % field == x

        r = self.next_wire()
        self.emit(f'  {r} <- @public({field_type});')
        self.instance_files[field_type].write(f'  < {x} >;\n')

        if field == 2:
            return BinaryWire(r, x, 2)
        else:
            return ArithmeticWire(r, x, field)

    # TODO: this assumes the default arithmetic field
    # is there a way to fix it if that's wrong?
    @functools.cache
    def constant_wire(self, e):
        field = self.fields[0]
        v = int(e) % field
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
        emp_bridge.setup_arith_zk(self.party)

    def __exit__(self, exception_type, exception_value, traceback):
        config.cc = None

        emp_bridge.finish_arith_zk()
