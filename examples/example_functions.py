from picozk import *
from picozk.functions import picozk_function
from picozk.sha256 import ZKSHA256

# @function(test, @out: 0:1, @in: 0:1)
#   $0 <- @mul($1, $1);
# @end

@picozk_function
def test_fn(x):
    return [x + x * x, x+5]

with PicoZKCompiler('picozk_test'):
    x = SecretInt(5)
    a, b = test_fn(x)
    reveal(a)

    c, d = test_fn(a)
    reveal(b)

