from numba import jit, config
config.DISABLE_JIT = True

from dataclasses import dataclass
import pandas as pd
import numpy as np
import galois
from functools import wraps

# Current compiler
cc = None

gensym_num = 0
def gensym(x):
    global gensym_num
    gensym_num = gensym_num + 1
    return f'{x}_{gensym_num}'


def picowizpl_function(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        raise RuntimeError('Args required')

    print('wrapper!', args, kwargs)
    def decorator(func):
        needs_compilation = True
        name = gensym('func')
        iw = kwargs['in_wires']
        ow = kwargs['out_wires']
        abs_fn = kwargs['abstraction']

        @wraps(func)
        def wrapped(*args):
            global cc
            nonlocal needs_compilation
            if needs_compilation:
                print('compiling', name)
                needs_compilation = False
                cc.emit(f'  @function({name}, @out: 0:{ow}, @in: 0:{iw}, 0:{iw})')
                # compile the function
                # TODO: generalize to n args
                # TODO: need generic wire bundles
                in_wires_1 = [f'${w}' for w in range(ow, ow+iw)]
                in_wires_2 = [f'${w}' for w in range(ow+iw, ow+2*iw)]
                in1 = BinaryInt([Wire(w, ow.val) for w, v in zip(in_wires_1, args[0])])
                in2 = BinaryInt([Wire(w, ow.val) for w, v in zip(in_wires_2, args[1])])
                print(in1)
                print(in2)
                1/0
                old_current_wire = cc.current_wire
                cc.current_wire = ow + 2*iw
                output = func(*args)
                cc.current_wire = old_current_wire
                # done compiling
                cc.emit(f'  @end')
                return output
            else:
                wires = [cc.next_wire() for _ in range(ow)]
                output = abs_fn(wires, *args)
                print(len(args))
                new_args = ', '.join([f'{i.wires[0].wire} .. {i.wires[-1].wire}' for i in args])
                cc.emit(f'  {wires[0]} .. {wires[-1]} <- @call({name}, {new_args});')
                return output

            # result = Prim('rec', [name, bound, list(args), func], None)
            # return result
        return wrapped

    return decorator

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
        if other == 0:
            return self
        else:
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
        if other == 0:
            return 0
        else:
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

