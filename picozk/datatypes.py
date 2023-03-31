from picozk import *

class ZKStack:
    def __init__(self, max_size):
        self.ram = ZKRAM(max_size+1)
        self.top = 0

    def cond_pop(self, cond):
        self.top = mux(cond & ~(self.top == 0), self.top - 1, self.top)
        return mux(cond, self.ram.read(self.top), 0)

    def cond_push(self, cond, v):
        self.top = mux(cond, self.top + 1, self.top)
        self.ram.write(self.top, mux(cond, v, self.ram.read(self.top)))

    def empty(self):
        return self.top == 0

    def pop(self):
        return self.cond_pop(1)

    def push(self, v):
        self.cond_push(1, v)

    def __str__(self):
        return f'ZKStack({self.ram.val[1:val_of(self.top)+1]})'

class ZKList:
    def __init__(self, xs):
        self.ram = ZKRAM(len(xs))
        for i, x in enumerate(xs):
            self.ram.write(i, SecretInt(x))

    def __getitem__(self, idx):
        return self.ram.read(idx)

    def __setitem__(self, idx, val):
        self.ram.write(idx, val)

    def __len__(self):
        return len(self.ram)

    def __str__(self):
        return f'ZKList({self.ram.val})'
