from dataclasses import dataclass
from typing import List
import functools
from picozk.wire import *
from picozk.binary_int import BinaryInt
from picozk import config

def SecretInt(x, field=None):
    return config.cc.add_to_witness(x, field)

def SecretBit(x):
    return config.cc.add_to_witness(x, 2)

def PublicInt(x, field=None):
    return config.cc.add_to_instance(x, field)

def PublicBit(x):
    return config.cc.add_to_instance(x, 2)

def reveal(x):
    config.cc.emit_gate('assert_zero', (x + (-val_of(x))).wire, effect=True, field=x.field)

def assert0(x):
    if val_of(x):
        raise Exception('Failed assert0!', x)

    config.cc.emit_gate('assert_zero', x.wire, effect=True, field=x.field)

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
    def __init__(self, file_prefix, field=2**61-1, options=[]):
        self.file_prefix = file_prefix
        self.current_wire = 0
        self.options = options

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

    def emit(self, s=''):
        if self.relation_file is None:
            return
        else:
            self.relation_file.write(s)
            self.relation_file.write('\n')

    def type_of(self, field):
        if field in self.fields:
            return self.fields[field]
        elif field == 2:
            return self.BINARY_TYPE
        else:
            raise Exception('no known type for field:', field)

    def emit_call(self, call, *args):
        if self.relation_file is None:
            return self.next_wire()
        else:
            args_str = ', '.join([str(a) for a in args])
            r = self.next_wire()
            self.emit(f'  {r} <- @call({call}, {args_str});')
            return r

    def emit_gate(self, gate, *args, effect=False, field=None):
        if self.relation_file is None:
            if effect:
                return
            else:
                return self.next_wire()
        else:
            if field is None:
                type_arg = 0
            else:
                type_arg = self.fields.index(field)

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

        # Open the witness files: one per field
        self.witness_files = []
        for t, field in enumerate(self.fields):
            f = open(self.file_prefix + f'.type{t}.wit', 'w')
            self.witness_files.append(f)

            f.write('version 2.2.0;\n')
            f.write('private_input;\n')
            f.write(f'@type field {field};\n')
            f.write('@begin\n')

        # Open the instance files: one per field
        self.instance_files = []
        for t, field in enumerate(self.fields):
            f = open(self.file_prefix + f'.type{t}.ins', 'w')
            self.instance_files.append(f)

            f.write('version 2.2.0;\n')
            f.write('public_input;\n')
            f.write(f'@type field {field};\n')
            f.write('@begin\n')

        self.relation_file = open(self.file_prefix + '.rel', 'w')

        self.emit('version 2.2.0;')
        self.emit('circuit;')
        self.emit('@plugin mux_v0;')

        if 'ram' in self.options:
            self.emit(f'@plugin ram_arith_v0;')

        if 'div' in self.options:
            self.emit(f'@plugin extended_arithmetic_v1;')

        for field in self.fields:
            self.emit(f'@type field {field};')

        if 'ram' in self.options:
            s = '@type @plugin(ram_arith_v0, ram, 0, {0}, {1}, {2});'
            self.emit(s.format(20, # number of rams
                               2000, # total allocation size
                               2000)) # not sure

        for t, field in enumerate(self.fields):
            if field != 2:
                bits_per_fe = util.get_bits_for_field(field)
                self.emit(f'@convert(@out: {t}:1, @in: {self.BINARY_TYPE}:{bits_per_fe});')
                self.emit(f'@convert(@out: {self.BINARY_TYPE}:{bits_per_fe}, @in: {t}:1);')
        # bits_per_fe = util.get_bits_for_field(self.field)
        # self.emit(f'@convert(@out: {self.ARITH_TYPE}:1, @in: {self.BINARY_TYPE}:{bits_per_fe});')
        # self.emit(f'@convert(@out: {self.BINARY_TYPE}:{bits_per_fe}, @in: {self.ARITH_TYPE}:1);')

        self.emit('@begin')

        self.emit('  @function(mux, @out: 0:1, @in: 0:1, 0:1, 0:1)')
        self.emit('    @plugin(mux_v0, permissive);')

        if 'ram' in self.options:
            self.emit(f'  @function(read_ram, @out: 0:1, @in: {self.RAM_TYPE}:1, 0:1)')
            self.emit('    @plugin(ram_arith_v0, read);')
            self.emit(f'  @function(write_ram, @in: {self.RAM_TYPE}:1, 0:1, 0:1)')
            self.emit('    @plugin(ram_arith_v0, write);')
            self.emit()

        if 'div' in self.options:
            for t, field in enumerate(self.fields):
                if field != 2:
                    self.emit(f'  // plugin function signature for division')
                    self.emit(f'  @function(plugin_div_{t}, @out: {t}:1, {t}:1, @in: {t}:1, {t}:1)')
                    self.emit(f'    @plugin(extended_arithmetic_v1, division);')
                    self.emit(f'  // wrapper for division without modulus')
                    self.emit(f'  @function(div_{t}, @out: {t}:1, @in: {t}:1, {t}:1)')
                    self.emit(f'    $0, $3 <- @call(plugin_div_{t}, $1, $2);')
                    self.emit(f'  @end')

                    self.no_convert_is_neg = True
                    bits_per_fe = util.get_bits_for_field(self.fields[t])
                    self.emit(f'  // plugin function for bit decomposition')
                    self.emit(f'  @function(plugin_decomp_{t}, @out: {t}:{bits_per_fe}, @in: {t}:1)')
                    self.emit(f'    @plugin(extended_arithmetic_v1, bit_decompose);')
                    self.emit(f'  @function(is_neg_{t}, @out: {t}:1, @in: {t}:1)')
                    self.emit(f'    $2...${1 + bits_per_fe} <- @call(plugin_decomp_{t}, $1);')
                    self.emit(f'    $0 <- {t}:$2;')
                    self.emit(f'  @end')

    def __exit__(self, exception_type, exception_value, traceback):
        config.cc = None

        self.emit('@end')

        for f in self.witness_files:
            f.write('@end\n')
            f.close()

        for f in self.instance_files:
            f.write('@end\n')
            f.close()

        self.relation_file.close()

