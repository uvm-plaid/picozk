from picowizpl import RAM, SecretInt

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
