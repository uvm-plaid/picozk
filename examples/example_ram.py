from picowizpl import *
import picowizpl.compiler

class RAM:
    def __init__(self, size):
        self.cc = picowizpl.compiler.cc
        self.size = size
        ram_type = 1
        self.wire = self.cc.next_wire()
        rn = self.wire.replace('$', '')
        self.cc.emit()
        self.cc.emit(f'  @function(init_ram_{rn}, @out: {ram_type}:1, @in: 0:1)')
        self.cc.emit(f'    @plugin(ram_arith_v0, init, {self.size});')
        self.cc.emit()

        self.cc.emit(f'  {self.wire} <- @call(init_ram_{rn}, {self.cc.wire_of(0)});')
        self.cc.emit()
        self.val = [None for _ in range(size)]

    def write(self, idx, val):
        emit(f'  @call(write_ram, {self.wire}, {self.cc.wire_of(idx)}, {self.cc.wire_of(val)});')
        self.val[idx] = val_of(val)

    def read(self, idx):
        r = self.cc.next_wire()
        emit(f'  {r} <- @call(read_ram, {self.wire}, {self.cc.wire_of(idx)});')
        return Wire(r, self.val[val_of(idx)])

class SecretIndexList:
    def __init__(self, xs):
        self.ram = RAM(len(xs))
        for i, x in enumerate(xs):
            self.ram.write(i, SecretInt(x))
        self.val = xs.copy()

    def __getitem__(self, idx):
        return self.ram.read(idx)

    def __str__(self):
        return f'SecretIndexList({self.val})'


with PicoWizPLCompiler('miniwizpl_test', options=['ram']):
    x = SecretIndexList([1,2,3,4,5])
    print(x)
    print(x[3])
