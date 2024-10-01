import numpy as np
from picozk import *
import picozk.poseidon_hash.poseidon_round_numbers as rn
import picozk.poseidon_hash.poseidon_round_constants as rc
import galois
from math import log2, ceil

from picozk import config
from picozk.functions import picozk_function

def dot(v, m):
    return [sum([a + b for a, b in zip(v, r)]) for r in m]

class PoseidonHash:
    def __init__(self, p, alpha, input_rate, t=None, security_level = 128):
        self.p = p
        self.security_level = security_level
        self.prime_bit_len = ceil(log2(p))

        if alpha > 1 and np.gcd(alpha, p-1) == 1:
            self.alpha = alpha
        else:
            raise RuntimeError("Not available alpha")

        self.input_rate = input_rate
        if t == None:
            self.t = input_rate
        else:
            self.t = t
        self.field_p = galois.GF(p)

        if 2 ** self.security_level > self.p ** self.t:
            raise RuntimeError("Not secure")

        self.full_round, self.partial_round, self.half_full_round = \
          rn.calc_round_numbers(log2(self.p),
                                security_level,
                                self.t, self.alpha, True)

        self.rc_field = rc.calc_round_constants(self.t,
                                                self.full_round,
                                                self.partial_round,
                                                self.p,
                                                self.field_p,
                                                self.alpha,
                                                self.prime_bit_len)
        self.rc_field = [int(x) for x in self.rc_field]
        self.mds_matrix = rc.mds_matrix_generator(self.field_p, self.t)
        self.mds_matrix = [[int(x) for x in y] for y in self.mds_matrix]

        self.state = [0 for _ in range(self.t)]

    def s_box(self, element):
        return pow(element, self.alpha, self.p)

    def full_rounds(self):
        for r in range(0, self.half_full_round):
            for i in range(0, self.t):
                self.state[i] = self.state[i] + self.rc_field[self.rc_counter]
                self.rc_counter += 1

                self.state[i] = self.s_box(self.state[i])

            self.state = dot(self.state, self.mds_matrix)

    def partial_rounds(self):
        for r in range(0, self.partial_round):
            for i in range(0, self.t):
                self.state[i] = self.state[i] + self.rc_field[self.rc_counter]
                self.rc_counter += 1
            self.state[0] = self.s_box(self.state[0])

            self.state = dot(self.state, self.mds_matrix)

    def hash_block(self, input_block, current_state):
        assert len(input_block) == self.t
        self.rc_counter = 0

        self.state = [input_block[i] + current_state[i] for i in range(self.t)]

        self.full_rounds()
        self.partial_rounds()
        self.full_rounds()

        return self.state

    def hash(self, input_vec):
        padded = input_vec + [0 for _ in range(self.t- (len(input_vec) % self.t))]
        blocks = [padded[i * self.t:(i + 1) * self.t]
                  for i in range((len(padded) + self.t - 1) // self.t )]
        for i, b in enumerate(blocks):
            self.state = self.hash_block(b, self.state)

        return self.state[1]

class BufferedPoseidonHash:
    def __init__(self, p, alpha, input_rate, t=None, security_level = 128):
        self.hash_func = PoseidonHash(p, alpha, input_rate, t, security_level)
        self.buf = []
        self.hash_func.state = [PublicInt(0) for s in self.hash_func.state]

    def hash(self, input_vec):
        for x in input_vec:
            assert isinstance(x, Wire), f'All inputs to hash_compact must be wires'

        self.buf.extend(input_vec)
        t = self.hash_func.t

        while len(self.buf) >= t:
            self.hash_block(self.buf[:t])
            self.buf = self.buf[t:]

    @picozk_function
    def _do_hash(self, input_block, current_state):
        return self.hash_func.hash_block(input_block, current_state)

    def hash_block(self, block):
        self.hash_func.state = self._do_hash(block, self.hash_func.state)

    def get_digest(self):
        if len(self.buf) > 0:
            t = self.hash_func.t
            assert len(self.buf) < t

            padding = [PublicInt(0) for _ in range(t - (len(self.buf) % t))]
            self.hash(padding)

        return self.hash_func.state[1]
