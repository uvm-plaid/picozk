from picozk import *
import ecdsa
from random import randrange
from ecdsa import numbertheory

from dataclasses import dataclass


p = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1


@dataclass
class CurvePoint:
    is_infinity: BooleanWire
    x: ArithmeticWire
    y: ArithmeticWire

    def mux(self, cond, other):
        return CurvePoint(mux_bool(cond, self.is_infinity, other.is_infinity),
                          mux(cond, self.x, other.x),
                          mux(cond, self.y, other.y))

    def double(self):
        a = 0
        l = ((3*(self.x*self.x) + a) * modular_inverse(2*self.y, p)) % p

        x3 = (l * l) - (2 * self.x)
        y3 = (l * (self.x - x3) - self.y)
        return CurvePoint(self.is_infinity, x3 % p, y3 % p)

    def add(self, other):
        assert isinstance(other, CurvePoint)
        assert val_of(self.is_infinity) == False
        assert val_of(self.x) != val_of(other.x) or val_of(self.y) != val_of(other.y)
        l = ((other.y - self.y) * modular_inverse(other.x - self.x, p)) % p
        x3 = l*l - self.x - other.x
        y3 = l * (self.x - x3) - self.y
        return self.mux(other.is_infinity, CurvePoint(False, x3 % p, y3 % p))

    def scale(self, s):
        bits = s.to_binary()
        res = CurvePoint(True, 0, 0)
        temp = self
        for b in reversed(bits.wires):
            res = temp.add(res).mux(b.to_bool(), res)
            temp = temp.double()
        return res


g = ecdsa.ecdsa.generator_secp256k1
n = g.order()
secret = randrange( 1, n )
pubkey = ecdsa.ecdsa.Public_key( g, g * secret )
privkey = ecdsa.ecdsa.Private_key( pubkey, secret )

h = 13874918263
sig = privkey.sign(h, randrange(1,n))

def verify(signature, hash_val, pubkey):
    r = signature.r
    s = signature.s

    c = util.modular_inverse(s, n)
    u1 = SecretInt((hash_val * c) % n)  # TODO: need field switching
    u2 = SecretInt((r * c) % n)

    sg = CurvePoint(False, g.x(), g.y())
    spk = CurvePoint(False, pubkey.point.x(), pubkey.point.y())

    #xy = u1 * g + u2 * pubkey.point
    xy1 = sg.scale(u1)
    xy2 = spk.scale(u2)
    xy = xy1.add(xy2)

    return xy.x == r

with PicoZKCompiler('picozk_test', field=p):
    result = verify(sig, h, pubkey)
    print(result)
    assert0(~result)
