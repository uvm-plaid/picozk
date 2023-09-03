from picozk import *
import numpy as np

# Freivalds' algorithm for probabilistic verification of matrix multiplication
# See Section 3.3, https://eprint.iacr.org/2021/730.pdf

n = 35
m = 40
l = 50

p = 2**61-1

def int_matrix(m):
    intv = np.vectorize(int)
    return np.array(intv(m).tolist(), dtype=object)

a = int_matrix(np.random.randint(0, p, (n, m)))
b = int_matrix(np.random.randint(0, p, (m, l)))
c = a @ b

zk_matrix = np.vectorize(SecretInt, otypes=[Wire])

with PicoZKCompiler('picozk_test'):
    zk_a = zk_matrix(a)
    zk_b = zk_matrix(b)

    # Requires 70,000 multiplication gates
    # zk_c = zk_a @ zk_b

    # Requires 5136 multiplication gates
    new_zk_c = zk_matrix(c%p)
    u = np.random.randint(0, p, n)
    v = np.random.randint(0, p, l)

    r1 = u @ zk_a @ zk_b @ v.T
    r2 = u @ new_zk_c @ v.T

    assert0(r1-r2)
