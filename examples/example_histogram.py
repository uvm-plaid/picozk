from picozk import *
from picozk.poseidon_hash import PoseidonHash

import pandas as pd

p = 2**61-1

with PicoZKCompiler('picozk_test', field=p, options=['ram']):
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv

    # Read the data
    df = pd.read_csv('ma2019.csv')
    sdf, _ = df['PUMA'].factorize()
    sdf = pd.Series(sdf).apply(SecretInt)

    # Hash the data
    poseidon_hash = PoseidonHash(p, alpha = 17, input_rate = 3)
    digest = poseidon_hash.hash(list(sdf))
    reveal(digest)

    # Query the data
    histogram = ZKList([0,0,0,0,0])

    def update_hist(x):
        histogram[x] = histogram[x] + 1

    sdf.apply(update_hist)

    # Reveal the histogram
    for i in range(5):
        reveal(histogram[i])

    print(histogram)
