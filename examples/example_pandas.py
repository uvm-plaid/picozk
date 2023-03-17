
from picowizpl import *
from picowizpl.poseidon_hash import PoseidonHash

import pandas as pd

p = 2**61-1

with PicoWizPLCompiler('miniwizpl_test', field=p):
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv('ma2019.csv')
    print('data length:', len(df))

    # Convert the PUMA code to an integer
    # PUMA 25-00703 is Essex County (East)
    # it includes Salem, Beverly, Gloucester & Newburyport
    # PUMA 25-00703 is transformed to the number 1
    df['PUMA'], codes = df['PUMA'].factorize()

    # OWN_RENT column is 1 if individual owns their home
    # Desired columns: PUMA and OWN_RENT
    df = df[['PUMA', 'OWN_RENT']]

    # Encode the data in the witness
    sdf = df.applymap(SecretInt)

    # Hash the data
    poseidon_hash = PoseidonHash(p, alpha = 17, input_rate = 3)
    digest = poseidon_hash.hash(list(sdf['PUMA']) + list(sdf['OWN_RENT']))
    reveal(digest)

    # Filter in the rows that have the correct PUMA and OWN_RENT values
    homeowner_rows = sdf.apply(lambda row: ((row['PUMA'] == 1) & (row['OWN_RENT'] == 1)).to_arith(),
                               axis=1)
    renter_rows = sdf.apply(lambda row: ((row['PUMA'] == 1) & (row['OWN_RENT'] == 2)).to_arith(),
                            axis=1)
    # Sum the filtered rows to get the total population
    total_homeowners = homeowner_rows.sum()
    total_renters = renter_rows.sum()
    print(total_homeowners)
    print(total_renters)
    reveal(total_homeowners)
    reveal(total_renters)


