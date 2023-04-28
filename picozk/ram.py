from .wire import *
from . import config

class ZKRAM:
    def __init__(self, size):
        self.cc = config.cc
        self.size = size
        self.wire = self.cc.next_wire()
        rn = self.wire.replace('$', '')
        self.cc.emit()
        self.cc.emit(f'  @function(init_ram_{rn}, @out: {self.cc.RAM_TYPE}:1, @in: 0:1)')
        self.cc.emit(f'    @plugin(ram_arith_v0, init, {self.size});')
        self.cc.emit()

        self.cc.emit(f'  {self.wire} <- @call(init_ram_{rn}, {wire_of(0)});')
        self.cc.emit()
        self.val = [0 for _ in range(size)]

    def write(self, idx, val):
        self.cc.emit(f'  @call(write_ram, {self.wire}, {wire_of(idx)}, {wire_of(val)});')
        self.val[val_of(idx)] = val_of(val)

    def read(self, idx):
        r = self.cc.next_wire()
        self.cc.emit(f'  {r} <- @call(read_ram, {self.wire}, {wire_of(idx)});')
        return ArithmeticWire(r, self.val[val_of(idx)], self.cc.fields[0])

    def __len__(self):
        return self.size
