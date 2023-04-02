#!/usr/bin/python3

__base__ = 'https://github.com/thomdixon/pysha2/blob/master/sha2/sha256.py'
__author__ = 'Lukas Prokop'
__license__ = 'MIT'

import copy
import struct
import binascii
import sys

from picozk import *
from picozk import util

F32 = 0xFFFFFFFF
goal = [3820012610, 2566659092, 2600203464, 2574235940, 665731556, 1687917388, 2761267483, 2018687061]

_k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
      0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
      0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
      0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
      0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
      0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
      0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
      0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
      0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

_h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]


def _pad(msglen):
    mdi = msglen & 0x3F
    print('pad mdi:', mdi)
    length = struct.pack('!Q', msglen << 3)
    print('length', length)

    if mdi < 56:
        padlen = 55 - mdi
    else:
        padlen = 119 - mdi

    return b'\x80' + (b'\x00' * padlen) + length


def _rotr(x, y):
    return ((x >> y) | (x << (32 - y))) & F32

def _maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)


def _ch(x, y, z):
    return (x & y) ^ ((~x) & z)

def print_word(x):
    assert isinstance(x, BinaryInt)
    bits = [val_of(b) for b in x.wires]
    return util.decode_int(bits)

def print_words(xs):
    return [print_word(x) for x in xs]


class ZKSHA256:
    def __init__(self):
        self._h = [BinaryInt(util.encode_int(x, 2**32)) for x in _h]

    def compress(self, chunk):
        w = [BinaryInt([0 for _ in range(32)]) for _ in range(64)]
        w[0:15] = chunk
        print('w IS:', print_words(w))

        for i in range(16, 64):
            s0 = w[i-15].rotr(7) ^ w[i-15].rotr(18) ^ (w[i-15] >> 3)
            s1 = w[i-2].rotr(17) ^ w[i-2].rotr(19) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1)

        a, b, c, d, e, f, g, h = self._h
        k = [BinaryInt(util.encode_int(x, 2**32)) for x in _k]

        for i in range(64):
            s0 = a.rotr(2) ^ a.rotr(13) ^ a.rotr(22)
            t2 = s0 + _maj(a, b, c)
            s1 = e.rotr(6) ^ e.rotr(11) ^ e.rotr(25)
            t1 = h + s1 + _ch(e, f, g) + k[i] + w[i]

            h = g
            g = f
            f = e
            e = (d + t1)
            d = c
            c = b
            b = a
            a = (t1 + t2)

        for i, (x, y) in enumerate(zip(self._h, [a, b, c, d, e, f, g, h])):
            self._h[i] = (x + y)

    def hash(self, msg):
        padding_amount = 512 - ((len(msg) + 1 + 64) % 512)
        padded_msg = msg + [1] + [0]*padding_amount + util.encode_int(len(msg), 2**64)
        assert len(padded_msg) % 512 == 0
        chunks = [padded_msg[i:i+512] for i in range(0, len(padded_msg), 512)]
        chunk_words = [[BinaryInt(chunk[i:i+32]) for i in range(0, len(chunk), 32)] for chunk in chunks]
        for chunk in chunk_words:
            self.compress(chunk)
        return self._h

with PicoZKCompiler('picozk_test', field=2**32):
    v = 2147483648
    v = 97
    x = SecretInt(v)
    xb = x.to_binary()
    bits = [SecretBit(x) for x in [0,1,1,0,0,0,0,1]]
    bs = [1,1,0,0,0,1,0,0,0,1,1,1,0,0,0,0,0,1,1,0,0,1,0,0,0,1,1,0,0,0,1,0,0,1,1,0,0,1,0,0,0,1,1,0,1,0,0,0,1,
          1,0,0,1,0,1,0,0,1,1,0,0,1,0,0,1,1,0,0,1,0,0,0,0,1,1,1,0,0,1,0,0,1,1,0,1,0,1,0,0,1,1,0,1,0,1,0,1,1,
          0,0,1,1,0,0,0,1,1,0,1,0,0,0,1,1,0,0,1,0,1,0,1,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,1,0,1,1,0,
          0,0,1,1,0,0,1,1,0,0,0,1,0,0,1,1,0,0,1,0,0,0,1,1,0,1,0,0,0,0,1,1,1,0,0,1,0,0,1,1,0,1,1,1,0,1,1,0,0,
          0,0,1,0,0,1,1,0,0,0,0,0,1,1,0,0,1,0,0,0,1,1,0,0,1,0,1,0,0,1,1,0,0,1,0,0,1,1,0,0,1,0,0,0,0,1,1,0,0,
          0,0,0,1,1,0,0,0,1,0,0,0,1,1,1,0,0,1,0,0,1,1,0,0,0,0,0,1,1,0,0,1,1,0,0,0,1,1,1,0,0,1,0,0,1,1,0,1,1,
          0,0,1,1,0,0,0,1,1,0,0,1,1,1,0,0,0,0,0,1,1,0,0,0,1,0,0,1,1,0,1,0,1,0,1,1,0,0,0,0,1,0,0,1,1,0,1,1,0,
          0,0,1,1,0,0,1,1,0,1,1,0,0,0,0,1,0,1,1,0,0,1,0,0,0,0,1,1,1,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,0,0,0,0,
          1,1,0,0,1,1,0,0,1,1,0,0,1,0,0,0,0,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,1,1,0,0,0,1,0,0,1,1,0,0,0,0,1,0,0,
          1,1,0,1,1,0,0,0,1,1,0,0,1,0,0,0,1,1,0,1,1,0,0,0,1,1,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,0,1,1,
          0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0]
    bits = [SecretBit(x) for x in bs]
    #print(xb.wires)
    h = ZKSHA256()
    #digest = h.hash(xb.wires)
    digest = h.hash(bits)
    print('done')
    print(len(digest))
    print(print_words(digest))


class SHA256:
    _output_size = 8
    blocksize = 1
    block_size = 64
    digest_size = 32

    def __init__(self, m=None):
        self._counter = 0
        self._cache = b''
        self._k = copy.deepcopy(_k)
        self._h = copy.deepcopy(_h)

        self.update(m)

    def _compress(self, c):
        w = [0] * 64

        w[0:16] = struct.unpack('!16L', c)
        print('w IS:', w)

        for i in range(16, 64):
            s0 = _rotr(w[i-15], 7) ^ _rotr(w[i-15], 18) ^ (w[i-15] >> 3)
            s1 = _rotr(w[i-2], 17) ^ _rotr(w[i-2], 19) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & F32

        a, b, c, d, e, f, g, h = self._h

        for i in range(64):
            s0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            t2 = s0 + _maj(a, b, c)
            s1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            t1 = h + s1 + _ch(e, f, g) + self._k[i] + w[i]

            h = g
            g = f
            f = e
            e = (d + t1) & F32
            d = c
            c = b
            b = a
            a = (t1 + t2) & F32

        for i, (x, y) in enumerate(zip(self._h, [a, b, c, d, e, f, g, h])):
            self._h[i] = (x + y) & F32

    def update(self, m):
        if not m:
            return

        print('message:', m, int.from_bytes(m, byteorder=sys.byteorder))
        print('bin:', bin(int.from_bytes(m, byteorder=sys.byteorder)))
        #print('message:', struct.unpack('!L', m))
        self._cache += m
        self._counter += len(m)

        while len(self._cache) >= 64:
            self._compress(self._cache[:64])
            self._cache = self._cache[64:]

    def digest(self):
        print('start digest')
        r = copy.deepcopy(self)
        r.update(_pad(self._counter))
        print('final:', r._h[:self._output_size])
        data = [struct.pack('!L', i) for i in r._h[:self._output_size]]
        return b''.join(data)

    def hexdigest(self):
        return binascii.hexlify(self.digest()).decode('ascii')


if __name__ == '__main__':
    def check(msg, sig):
        m = SHA256()
        m.update(msg.encode('ascii'))
        print(m.hexdigest() == sig)

    tests = {
        # "":
        #     'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        # "a":
        #     'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb',
        # "abc":
        #     'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
        # "message digest":
        #     'f7846f55cf23e14eebeab5b4e1550cad5b509e3348fbc4efa3a1413d393cb650',
        # "abcdefghijklmnopqrstuvwxyz":
        #     '71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2daf18b73',
        # "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789":
        #     'db4bfcbd4da0cd85a60c3c37d3fbd8805c77f15fc6b1fdfe614ee0a7c8fdb4c0',
        # ("12345678901234567890123456789012345678901234567890123456789"
        #  "012345678901234567890"):
        #     'f371bc4a311f2b009eef952dd83ca80e2b60026c8e935592d0f9c308453c813e',
        "00baf6626abc2df808da36a518c69f09b0d2ed0a79421ccfde4f559d2e42128b":
            'b835e56173be2b5b7177d71bf02850dc578ac855ac60f91a108eec253bd5a543'
    }

    for inp, out in tests.items():
        check(inp, out)
