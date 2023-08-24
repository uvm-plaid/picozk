from picozk import *

def zk_max(xs):
    # prover calculates the actual max and introduces it in the witness
    max_v = max([val_of(x) for x in xs])
    smax_v = SecretInt(max_v)

    # prove that every value in the list is not greater than the max
    for x in xs:
        assert0(x > smax_v)

    # prove that one of the values in the list is the max
    max_included = 1
    for x in xs:
        max_included = (x - smax_v)*max_included
    assert0(max_included)

    # return the max value
    return smax_v

with PicoZKCompiler('picozk_test'):
    xs = [1,2,3,4,5,6,7,8]
    sxs = [SecretInt(x) for x in xs]
    max_val = zk_max(sxs)
    print('max value:', max_val)
    assert0(max_val - 8)
