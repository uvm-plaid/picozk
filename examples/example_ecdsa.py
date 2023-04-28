from picozk import *
import ecdsa
from random import randrange
from ecdsa import numbertheory

from dataclasses import dataclass

# Curve & generator parameters
g = ecdsa.ecdsa.generator_secp256k1
p = g.curve().p()
n = g.order()

# Generate secret & public keys
secret = randrange( 1, n )
pubkey = ecdsa.ecdsa.Public_key( g, g * secret )
privkey = ecdsa.ecdsa.Private_key( pubkey, secret )

# Sign a hash value
h = 13874918263
sig = privkey.sign(h, randrange(1,n))

@dataclass
class CurvePoint:
    is_infinity: BooleanWire
    x: ArithmeticWire
    y: ArithmeticWire

    # Mux for a curve point
    def mux(self, cond, other):
        return CurvePoint(mux_bool(cond, self.is_infinity, other.is_infinity),
                          mux(cond, self.x, other.x),
                          mux(cond, self.y, other.y))

    # Point doubling
    def double(self):
        a = 0
        l = ((3*(self.x*self.x) + a) * modular_inverse(2*self.y, p)) % p

        x3 = (l * l) - (2 * self.x)
        y3 = (l * (self.x - x3) - self.y)
        return CurvePoint(self.is_infinity, x3 % p, y3 % p)

    # Point addition
    def add(self, other):
        assert isinstance(other, CurvePoint)
        assert val_of(self.is_infinity) == False
        assert val_of(self.x) != val_of(other.x) or val_of(self.y) != val_of(other.y)
        l = ((other.y - self.y) * modular_inverse(other.x - self.x, p)) % p
        x3 = l*l - self.x - other.x
        y3 = l * (self.x - x3) - self.y
        return self.mux(other.is_infinity, CurvePoint(False, x3 % p, y3 % p))

    # Point scaling by a scalar via repeated doubling
    def scale(self, s):
        bits = s.to_binary()
        res = CurvePoint(True, 0, 0)
        temp = self
        for b in reversed(bits.wires):
            res = temp.add(res).mux(b.to_bool(), res)
            temp = temp.double()
        return res

# Verify the ECDSA signature represented by (r, s)
def verify(r, s, hash_val, pubkey):
    c = modular_inverse(s, n)
    u1 = hash_val * c
    u2 = r * c

    u1_p = u1.to_binary().to_arithmetic(field=p)
    u2_p = u2.to_binary().to_arithmetic(field=p)

    sg = CurvePoint(False, g.x(), g.y())
    spk = CurvePoint(False, pubkey.point.x(), pubkey.point.y())

    xy1 = sg.scale(u1_p)
    xy2 = spk.scale(u2_p)
    xy = xy1.add(xy2)
    x_n = xy.x.to_binary().to_arithmetic(field=n)

    return x_n - r

# Example: secret signature, secret hash value; public pubkey
with PicoZKCompiler('picozk_test', field=[p,n]):
    sig_r = SecretInt(sig.r, field=n)
    sig_s = SecretInt(sig.s, field=n)
    secret_h = SecretInt(h, field=n)
    result = verify(sig_r, sig_s, secret_h, pubkey)
    assert0(result)
