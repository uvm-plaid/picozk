from picozk import *
from picozk import util
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

    # Point addition (self != other)
    def add_nonequal(self, other):
        assert isinstance(other, CurvePoint)
        assert val_of(self.x) != val_of(other.x) or val_of(self.y) != val_of(other.y)

        l = ((other.y - self.y) * modular_inverse(other.x - self.x, p)) % p
        x3 = l*l - self.x - other.x
        y3 = l * (self.x - x3) - self.y
        return self.mux(other.is_infinity,
                        other.mux(self.is_infinity,
                                  CurvePoint(False, x3 % p, y3 % p)))

    # Point addition (general)
    def add(self, other):
        assert isinstance(other, CurvePoint)

        # case 1: self == other
        case1_cond = (self.x == other.x) & (self.y == other.y)
        case1_point = self.double()

        # case 2: self != other
        case2_cond = ~case1_cond
        x_diff = mux(case1_cond, 1, other.x - self.x)
        l = ((other.y - self.y) * modular_inverse(x_diff, p)) % p
        x3 = l*l - self.x - other.x
        y3 = l * (self.x - x3) - self.y
        case2_point = CurvePoint(False, x3 % p, y3 % p)

        return self.mux(other.is_infinity,
                        other.mux(self.is_infinity,
                                  case1_point.mux(case1_cond, case2_point)))

    # Point scaling by a scalar via repeated doubling
    def scale(self, s):
        assert not val_of(self.is_infinity)

        if isinstance(s, ArithmeticWire):
            bits = s.to_binary()
            res = CurvePoint(True, 0, 0)
            temp = self
            for b in reversed(bits.wires):
                res = temp.add_nonequal(res).mux(b.to_bool(), res)
                temp = temp.double()
            return res
        elif isinstance(s, int):
            bits = util.encode_int(s, s)
            res = CurvePoint(True, 0, 0)
            temp = self
            for b in reversed(bits):
                if b:
                    res = temp.add_nonequal(res)
                temp = temp.double()
            return res
        else:
            raise Exception('Unsupported exponent:', s)


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
    # test addition
    inf = CurvePoint(SecretBit(1).to_bool(), 0, 0)
    a = CurvePoint(False, pubkey.point.x(), pubkey.point.y())
    reveal(inf.add(a).x)
    reveal(a.add(inf).x)

    # test public curve point operations
    e = 581672931
    b_pub = a.scale(e)
    a = CurvePoint(False, pubkey.point.x(), pubkey.point.y())
    b = a.scale(SecretInt(e))
    assert0(b_pub.x - b.x)
    assert0(b_pub.y - b.y)

    # test adding a point to itself
    c = CurvePoint(SecretBit(0).to_bool(), SecretInt(pubkey.point.x()), SecretInt(pubkey.point.y()))
    print(c.add(c).x)
    reveal(c.add(c).x)

    # verify a signature
    sig_r = SecretInt(sig.r, field=n)
    sig_s = SecretInt(sig.s, field=n)
    secret_h = SecretInt(h, field=n)
    result = verify(sig_r, sig_s, secret_h, pubkey)
    assert0(result)
