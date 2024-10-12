from dataclasses import dataclass
from typing import List
import functools
from picozk.wire import *
from picozk.binary_int import BinaryInt
from picozk import config
import sys

import emp_bridge

def SecretInt(x, field=None):
    return config.cc.add_to_witness(x, field)

def SecretBit(x):
    return config.cc.add_to_witness(x, 2)

def PublicInt(x, field=None):
    return config.cc.add_to_instance(x, field)

def PublicBit(x):
    return config.cc.add_to_instance(x, 2)

def reveal(x):
    rv = x.wire.reveal()
    assert val_of(x) == rv, f'Revealed value ({rv}) not equal to expected ({val_of(x)})!'
    return rv

def assert0(x):
    if val_of(x):
        raise Exception('Failed assert0!', x)

    rv = x.wire.reveal()
    assert rv == 0, f'assert0 failed with revealed value {rv}!'

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
    def __init__(self, filename, field=2**61-1, party=None, options=[]):
        self.current_wire = 0
        self.options = options
        if party is None:
            assert len(sys.argv) >= 2
            self.party = int(sys.argv[1])
            assert self.party in [1,2]
        else:
            self.party = party

    def add_to_witness(self, x, field):
        f = 2**61-1
        assert field == None or field == f
        print("Creating emp bridge val")
        emp_val = emp_bridge.EMPIntFp.from_constant(x%f, emp_bridge.ALICE)
        print("Success!")
        return ArithmeticWire(emp_val, x%f, f, self.party)

    def add_to_instance(self, x, field):
        f = 2**61-1
        assert field == None or field == f
        emp_val = emp_bridge.EMPIntFp.from_constant(x%f, emp_bridge.PUBLIC)
        return ArithmeticWire(emp_val, x%f, f, self.party)

    @functools.cache
    def constant_wire(self, e):
        f = 2**61-1
        v = int(e) % f
        emp_val = emp_bridge.EMPIntFp.from_constant(v, emp_bridge.PUBLIC)
        return ArithmeticWire(emp_val, v, f)

    def __enter__(self):
        global cc
        config.cc = self
        cc = self
        emp_bridge.setup_bool_zk(self.party)
        emp_bridge.setup_arith_zk(self.party, True)
        emp_bridge.sync_bool_zk()

    def __exit__(self, exception_type, exception_value, traceback):
        config.cc = None
        emp_bridge.finish_bool_zk()
        emp_bridge.finish_arith_zk()
