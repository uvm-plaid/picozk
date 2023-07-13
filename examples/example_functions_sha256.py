from picozk import *
from picozk.functions import picozk_function
from picozk.sha256 import ZKSHA256

# @function(test, @out: 0:1, @in: 0:1)
#   $0 <- @mul($1, $1);
# @end

@picozk_function
def run_hash(bits):
    h = ZKSHA256()
    digest = h.hash(bits)
    return digest


# @picozk_function
# def test_fn(x):
#     return x + x * x

with PicoZKCompiler('picozk_test'):
    # x = SecretInt(5)
    # a = test_fn(x)
    # reveal(a)

    # b = test_fn(a)
    # reveal(b)

    bs = [0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,1,0,0,1,1,0,0,0,0,1,0,1,1,0,0,1,1,0,0,0,
          1,1,0,1,1,0,0,0,1,1,0,1,1,0,0,0,1,1,0,0,1,0,0,0,1,1,0,1,1,0,0,1,1,0,0,0,0,1,0,1,1,0,
          0,0,1,0,0,1,1,0,0,0,1,1,0,0,1,1,0,0,1,0,0,1,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,1,1,0,
          0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,0,0,0,0,1,1,0,0,1,0,0,0,1,1,0,0,0,0,1,0,0,1,1,0,0,1,1,
          0,0,1,1,0,1,1,0,0,1,1,0,0,0,0,1,0,0,1,1,0,1,0,1,0,0,1,1,0,0,0,1,0,0,1,1,1,0,0,0,0,1,
          1,0,0,0,1,1,0,0,1,1,0,1,1,0,0,0,1,1,1,0,0,1,0,1,1,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,1,1,
          1,0,0,1,0,1,1,0,0,0,1,0,0,0,1,1,0,0,0,0,0,1,1,0,0,1,0,0,0,0,1,1,0,0,1,0,0,1,1,0,0,1,
          0,1,0,1,1,0,0,1,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,1,0,0,1,1,0,1,1,1,0,0,1,1,1,0,0,1,
          0,0,1,1,0,1,0,0,0,0,1,1,0,0,1,0,0,0,1,1,0,0,0,1,0,1,1,0,0,0,1,1,0,1,1,0,0,0,1,1,0,1,
          1,0,0,1,1,0,0,1,1,0,0,1,0,0,0,1,1,0,0,1,0,1,0,0,1,1,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,1,
          0,1,0,1,0,0,1,1,0,1,0,1,0,0,1,1,1,0,0,1,0,1,1,0,0,1,0,0,0,0,1,1,0,0,1,0,0,1,1,0,0,1,
          0,1,0,0,1,1,0,1,0,0,0,0,1,1,0,0,1,0,0,0,1,1,0,0,0,1,0,0,1,1,0,0,1,0,0,0,1,1,1,0,0,0,
          0,1,1,0,0,0,1,0]
    bits = [SecretBit(x) for x in bs]

    for _ in range(200):
        digest = run_hash(bits)

        for w in digest:
            for b in w.wires:
                reveal(b)
