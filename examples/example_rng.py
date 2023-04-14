from picozk import *
from picozk.poseidon_hash import PoseidonHash
import numpy as np

SCALE_FACTOR = 10000
p = 2**61-1
# bitwidth is 10

# Generate a lookup table for Laplace noise samples
def gen_laplace_table(sensitivity):
    # Convert a number into bits
    def bitfield(n):
        return [int(x) for x in '{0:010b}'.format(n)]

    # Convert bits into a decimal in [0,1]
    def bval(bits):
        tot = 0
        for i,b in zip(range(1, 11), bits):
            tot = tot + b/(2**i)
        return tot

    # Compute an entry in the lookup table
    def lap_draw(unif):
        U = unif-.5
        return sensitivity * np.sign(U) * np.log(1-2*np.abs(U))

    table = []
    for n in range(1, 1023):
        v = bval(bitfield(n))
        lap = lap_draw(v)

        # Encode as fixed-point number
        scaled = lap*SCALE_FACTOR
        encoded = scaled % p
        encoded = encoded % p
        table.append(encoded)

    return table

# Decode a fixed-point number
def decode(n):
    if n > p/2:
        return (n - p)/SCALE_FACTOR
    else:
        return n/SCALE_FACTOR

poseidon_hash = PoseidonHash(p, alpha = 17, input_rate = 3, t = 3)

with PicoZKCompiler('picozk_test', options=['ram']):
    seed = SecretInt(1987034928369859712)

    zk_lap_table = ZKList(gen_laplace_table(sensitivity=1))

    for _ in range(1000):
        digest = poseidon_hash.hash([seed])
        x = digest.to_binary()
        shifted_x = x >> 51

        # create a uniform draw in [0, 1023]
        U = shifted_x.to_arithmetic()

        # look up laplace sample in the table
        lap_draw = zk_lap_table[U]

        #print(decode(lap_draw.val))
        reveal(lap_draw)
