from picozk import *
from picozk.poseidon_hash import PoseidonHash

import pandas as pd

SCALE_FACTOR = 1000
p = 2**61-1
# bitwidth is 13

# Generate a lookup table for Laplace noise samples
def gen_laplace_table(sensitivity):
    # Convert a number into bits
    def bitfield(n):
        return [int(x) for x in '{0:013b}'.format(n)]

    # Convert bits into a decimal in [0,1]
    def bval(bits):
        tot = 0
        for i,b in zip(range(1, 14), bits):
            tot = tot + b/(2**i)
        return tot

    # Compute an entry in the lookup table
    def lap_draw(unif):
        U = unif-.5
        return sensitivity * np.sign(U) * np.log(1-2*np.abs(U))

    table = []
    for n in range(1, 8191):
        v = bval(bitfield(n))
        lap = lap_draw(v)

        # Encode as fixed-point number
        scaled = lap*SCALE_FACTOR
        encoded = scaled % p
        encoded = encoded % p
        table.append(encoded)

    return table

with PicoZKCompiler('picozk_test', field=p, options=['ram']):
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv('ma2019.csv')

    mapping = {
        '25-00703': 0,
        '25-00503': 1,
        '25-01300': 2,
        '25-02800': 3,
        '25-01000': 4
        }

    sdf = df['PUMA'].replace(mapping).apply(SecretInt)

    # Hash the data
    poseidon_hash = PoseidonHash(p, alpha = 17, input_rate = 3)
    digest = poseidon_hash.hash(list(sdf))
    reveal(digest)

    # Query the data
    histogram = ZKList([0,0,0,0,0])

    def update_hist(x):
        histogram[x] = histogram[x] + 1000

    sdf.apply(update_hist)
    print(histogram)

    # Add Laplace noise
    seed = SecretInt(1987034928369859712)

    zk_lap_table = ZKList(gen_laplace_table(sensitivity=1))
    rng_hash = PoseidonHash(p, alpha = 17, input_rate = 3, t = 3)

    for i in range(5):
        digest = poseidon_hash.hash([seed])
        x = digest.to_binary()
        shifted_x = x >> 48

        # create a uniform draw in [0, 1023]
        U = shifted_x.to_arithmetic()

        # look up laplace sample in the table
        lap_draw = zk_lap_table[U]
        histogram[i] = histogram[i] + lap_draw

    print(histogram)
    # Reveal the noisy histogram
    for i in range(5):
        reveal(histogram[i])

