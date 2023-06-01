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

def abs_fn(xs: List[Wire]) -> (List[str], List[int]):
    return [wire_of(x) for x in xs], [val_of(x) for x in xs]

def conc_fn(wires: List[str], vals: List[int]) -> List[Wire]:
    p = 2**61-1
    return [ArithmeticWire(w, v%p, p) for w, v in zip(wires, vals)]

def conc_in(wires, args):
    w_in1, w_in2 = wires
    obj, in1, in2 = args

    a_in1 = conc_fn(w_in1, in1)
    a_in2 = conc_fn(w_in2, in2)

    return (obj, a_in1, a_in2)

def abs_in(args):
    obj, in1, in2 = args

    wires1, vals1 = abs_fn(in1)
    wires2, vals2 = abs_fn(in2)

    return [wires1, wires2], (obj, vals1, vals2)

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


    # @picozk_function(abs_fns  = [abs_in, abs_fn],
    #                  conc_fns = [conc_in, conc_fn],
    #                  in_wires = [3, 3], out_wires=3)
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
