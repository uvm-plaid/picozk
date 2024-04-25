from functools import wraps
from io import StringIO

import picozk
from picozk import util, config
from picozk.wire import *

use_numpy = True
try:
    import numpy as np
except ImportError:
    use_numpy = False

def picozk_function(func):
    name = util.gensym('func')
    needs_compiling = True
    num_input_wires = None
    num_output_wires = None

    def _extract_wires(v):
        if isinstance(v, Wire):
            return [v]
        elif isinstance(v, (tuple, list)):
            l = [_extract_wires(i) for i in v]
            return [item for sublist in l for item in sublist]
        elif use_numpy and isinstance(v, np.ndarray):
            l = [_extract_wires(i) for i in v]
            return [item for sublist in l for item in sublist]
        elif isinstance(v, BinaryInt):
            return _extract_wires(v.wires)
        elif isinstance(v, (int, float, bool)):
            return []
        elif v is None:
            return []
        elif str(type(v)) == "<class 'picozk.sha256.BufferedZKSHA256'>":
            return []
        elif str(type(v)) == "<class 'picozk.poseidon_hash.poseidon_hash.BufferedPoseidonHash'>":
            return []
        else:
            raise Exception('unsupported type:', type(v), v)

    def _freshen_wires(v, wires):
        if isinstance(v, Wire):
            w = config.cc.next_wire()
            new_wire = type(v)(f'{w}', v.val, v.field)
            wires[v] = new_wire
            return new_wire
        elif isinstance(v, tuple):
            return tuple([_freshen_wires(i, wires) for i in v])
        elif isinstance(v, list):
            return [_freshen_wires(i, wires) for i in v]
        elif use_numpy and isinstance(v, np.ndarray):
            return np.array([_freshen_wires(i, wires) for i in v])
        elif isinstance(v, BinaryInt):
            return BinaryInt([_freshen_wires(i, wires) for i in v.wires])
        elif isinstance(v, (int, float, bool)):
            return v
        elif v is None:
            return None
        elif str(type(v)) == "<class 'picozk.sha256.BufferedZKSHA256'>":
            return v
        elif str(type(v)) == "<class 'picozk.poseidon_hash.poseidon_hash.BufferedPoseidonHash'>":
            return v
        else:
            raise Exception('unsupported type:', str(type(v)), v)

    def _run_function(args):
        cc = config.cc
        # get the input wires
        input_wire_wires = [w.wire for w in _extract_wires(args)]
        assert len(input_wire_wires) == num_input_wires, \
               f'Function expected {num_input_wires} input wires, got {len(input_wire_wires)}'
        input_wires = ', '.join(input_wire_wires)

        # set up the compiler
        old_current_wire = cc.current_wire
        cc.current_wire = 5000
        cc.constant_wire.cache_clear()
        old_relation_file = cc.relation_file
        cc.relation_file = None

        # run the function
        output = func(*args)

        # reset the compiler
        cc.current_wire = old_current_wire
        cc.relation_file = old_relation_file
        cc.constant_wire.cache_clear()

        # handle the output
        context_map = {}
        output_value = _freshen_wires(output, context_map)
        output_wires = [w.wire for w in context_map.values()]
        assert len(output_wires) == num_output_wires, \
               f'Function expected {num_output_wires} output wires, got {len(output_wires)}'
        output_spec = ', '.join(output_wires)

        call_spec = [name]
        if len(input_wire_wires) > 0:
            call_spec.append(input_wires)
        call_spec_str = ', '.join(call_spec)

        if len(output_wires) == 0:
            cc.emit(f'  @call({call_spec_str});')
        else:
            cc.emit(f'  {output_spec} <- @call({call_spec_str});')

        return output_value

    def _compile_function(args):
        nonlocal num_input_wires
        nonlocal num_output_wires

        # set up the compiler to compile a function
        cc = config.cc
        old_current_wire = cc.current_wire
        cc.current_wire = 5000
        cc.constant_wire.cache_clear()
        old_relation_file = cc.relation_file
        buf = StringIO("")
        cc.relation_file = buf

        # find wires in the inputs
        input_map = {}
        inputs = _freshen_wires(args, input_map)
        num_input_wires = len(input_map)

        # replace input wires with fresh numbers
        saved_input_wires = []
        for old, new in input_map.items():
            saved_input_wires.append(old.wire)
            old.wire = new.wire

        # run the function
        output = func(*args)

        # restore the old numbers on the input wires
        for old, saved in zip(input_map.keys(), saved_input_wires):
            old.wire = saved

        # handle the output
        output_map = {}
        cc.current_wire = 0
        extracted_output = _freshen_wires(output, output_map)
        num_output_wires = len(output_map) if extracted_output is not None else 0

        for old, new in output_map.items():
            t = cc.fields.index(old.field)
            cc.emit(f'  {new.wire} <- {t}:{old.wire};')

        # print the function
        cc.relation_file = old_relation_file
        output_spec = ', '.join([f'{cc.fields.index(w.field)}:1' for w in output_map.values()])
        input_spec = ', '.join([f'{cc.fields.index(w.field)}:1' for w in input_map.values()])

        fn_spec = [name]
        if len(output_map.values()) > 0:
            fn_spec.append(f'@out: {output_spec}')
        if len(input_map.values()) > 0:
            fn_spec.append(f'@in: {input_spec}')

        fn_spec_str = ', '.join(fn_spec)
        cc.emit(f'\n @function({fn_spec_str})')

        for i, w in enumerate(input_map.values()):
            t = cc.fields.index(w.field)
            cc.emit(f'  {w.wire} <- {t}:${i + len(output_map)};')

        buf.seek(0)
        cc.emit(buf.read())
        cc.emit(' @end\n')

        # reset the compiler
        cc.current_wire = old_current_wire
        cc.constant_wire.cache_clear()

        # print the function call
        input_wires = ', '.join([w.wire for w in input_map.keys()])
        context_map = {}
        output_value = _freshen_wires(output, context_map)
        output_wires = [w.wire for w in context_map.values()]
        output_spec = ', '.join(output_wires)

        call_spec = [name]
        if len(input_map.keys()) > 0:
            call_spec.append(input_wires)
        call_spec_str = ', '.join(call_spec)

        if len(output_wires) == 0:
            cc.emit(f'  @call({call_spec_str});')
        else:
            cc.emit(f'  {output_spec} <- @call({call_spec_str});')

        return output_value

    @wraps(func)
    def wrapped(*args):
        nonlocal needs_compiling
        cc = config.cc

        if needs_compiling:
            output_value = _compile_function(args)
            needs_compiling = False
        else:
            output_value = _run_function(args)

        return output_value

    return wrapped
