from picowizpl import *

class SecretStack:
    def __init__(self, max_size):
        self.ram = RAM(max_size)
        self.size = 0

    def pop(self):
        self.size = mux(self.size == 0, 0, self.size - 1)
        return self.ram.read(self.size)

    def push(self, v):
        self.ram.write(self.size, v)
        self.size = self.size + 1

    def cond_pop(self, cond):
        old_size = self.size
        self.size = mux(cond, self.size - 1, self.size)
        self.size = mux(old_size == 0, 0, self.size)
        return mux(cond, self.ram.read(self.size), 0)

    def cond_push(self, cond, v):
        self.size = mux(cond, self.size + 1, self.size)
        old_val = self.ram.read(self.size)
        self.ram.write(self.size, mux(cond, v, old_val))

class SecretIndexList:
    def __init__(self, xs):
        self.ram = RAM(len(xs))
        for i, x in enumerate(xs):
            self.ram.write(i, SecretInt(x))

    def __getitem__(self, idx):
        return self.ram.read(idx)

    def __setitem__(self, idx, val):
        self.ram.write(idx, val)

    def __str__(self):
        return f'SecretIndexList({self.ram.val})'
