from picozk import *
import numpy as np

# Freivalds' algorithm for probabilistic verification of matrix multiplication
# See Section 3.3, https://eprint.iacr.org/2021/730.pdf

n = 40
m = 50
l = 35

a = np.random.randint(0, 1000, (n, m))
b = np.random.randint(0, 1000, (m, l))
c = a @ b

zk_matrix = np.vectorize(SecretInt, otypes=[Wire])

with PicoZKCompiler('picozk_test'):
    zk_a = zk_matrix(a)
    zk_b = zk_matrix(b)

    # Requires 70,000 multiplication gates
    # zk_c = zk_a @ zk_b

    # Requires 5136 multiplication gates
    new_zk_c = zk_matrix(c)
    u = np.random.randint(0, 1000, n)
    v = np.random.randint(0, 1000, l)

    mat1 = u @ zk_a @ zk_b @ v.T
    mat2 = u @ new_zk_c @ v.T

    assert0(mat1-mat2)
