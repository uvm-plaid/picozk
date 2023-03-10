from functools import wraps
import picowizpl
from picowizpl import Wire, WireBundle
import util

def picowizpl_function(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        raise RuntimeError('Args required')

    def decorator(func):
        needs_compilation = True
        name = util.gensym('func')
        iw = kwargs['in_wires']
        ow = kwargs['out_wires']
        abs_op = kwargs['op']
        absfn = kwargs['absfn']
        concfn = kwargs['concfn']

        @wraps(func)
        def wrapped(*args):
            nonlocal needs_compilation
            cc = picowizpl.cc

            if needs_compilation:
                needs_compilation = False
                cc.emit(f'  @function({name}, @out: 0:{ow}, @in: 0:{iw}, 0:{iw})')
                # generate the arguments
                new_args = []
                for i, a in enumerate(args):
                    wire_names = [f'${w}' for w in range(ow + i*iw, ow + (i+1)*iw)]
                    wire_bundle = concfn(a)
                    new_wires = [Wire(name, w.val) for name, w in zip(wire_names, wire_bundle.wires)]
                    new_args.append(absfn(WireBundle(new_wires)))

                # set up the compiler
                old_current_wire = cc.current_wire
                cc.current_wire = ow + 2*iw
                # compile the function
                output = func(*new_args)
                output_wire_names = [f'${w}' for w in range(0, ow)]
                for output_wire_name, wire in zip(output_wire_names, concfn(output).wires):
                    cc.emit(f'  {output_wire_name} <- {wire.wire};')

                # done compiling
                cc.emit(f'  @end')

                # reset the compiler
                cc.current_wire = old_current_wire
                return output
            else:
                wires = [cc.next_wire() for _ in range(ow)]
                output = abs_op(wires, *args)
                new_args = ', '.join([f'{i.wires[0].wire} .. {i.wires[-1].wire}' for i in args])
                cc.emit(f'  {wires[0]} .. {wires[-1]} <- @call({name}, {new_args});')
                return output

        return wrapped

    return decorator
