from functools import wraps
import picozk
from . import util
from . import config
from .wire import *

def picozk_function(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        raise RuntimeError('Args required')

    def decorator(func):
        needs_compilation = True
        name = util.gensym('func')
        iw = kwargs['in_wires']
        ow = kwargs['out_wires']

        abs_in, abs_fn   = kwargs['abs_fns']
        conc_in, conc_fn = kwargs['conc_fns']

        @wraps(func)
        def wrapped(*args):
            nonlocal needs_compilation
            cc = config.cc

            if needs_compilation:
                needs_compilation = False
                in_str = ', '.join([f'0: {w}' for w in iw])
                cc.emit(f'  @function({name}, @out: 0:{ow}, @in: {in_str})')

                # generate the arguments
                new_args = []
                cw = ow
                in_wire_names = []
                for nw in iw:
                    if nw == 1:
                        in_wire_names.append(f'${cw}')
                    else:
                        in_wire_names.append([f'${w}' for w in range(cw, cw+nw)])
                    cw = cw + nw

                # set up the compiler
                old_current_wire = cc.current_wire
                cc.current_wire = cw
                cc.constant_wire.cache_clear()

                # generate the input
                _, in_vals = abs_in(args)
                new_args = conc_in(in_wire_names, in_vals)

                # compile the function
                output = func(*new_args)
                output_wires, _ = abs_fn(output)

                if ow == 1:
                    cc.emit(f'  $0 <- {output_wires};')
                else:
                    output_wire_names = [f'${w}' for w in range(0, ow)]
                    for output_wire_name, wire in zip(output_wire_names, output_wires):
                        cc.emit(f'  {output_wire_name} <- {wire};')

                # done compiling
                cc.emit(f'  @end')

                # reset the compiler
                cc.constant_wire.cache_clear()
                cc.current_wire = old_current_wire


            # construct the function call
            in_wires, abs_input = abs_in(args)
            output = func(*abs_input)

            input_args = []
            for wnum, wires in zip(iw, in_wires):
                if wnum == 1:
                    input_args.append(wires)
                else:
                    wire_names = [cc.next_wire() for _ in range(wnum)]
                    wire_range = f'{wire_names[0]} ... {wire_names[-1]}'
                    cc.emit(f'  @new({wire_range});')
                    for wnew, wold in zip(wire_names, wires):
                        cc.emit(f'  {wnew} <- {wold};')
                    input_args.append(wire_range)

            new_args = ', '.join(input_args)

            if ow == 1:
                output_wire = cc.next_wire()
                cc.emit(f'  {output_wire} <- @call({name}, {new_args});')
                conc_output = conc_fn(output_wire, output)
            else:
                output_wires = [cc.next_wire() for _ in range(ow)]
                cc.emit(f'  {output_wires[0]} ... {output_wires[-1]} <- @call({name}, {new_args});')
                conc_output = conc_fn(output_wires, output)

            return conc_output

        return wrapped

    return decorator
