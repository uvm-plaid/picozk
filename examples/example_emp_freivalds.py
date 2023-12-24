import picozk as pzk
import numpy as np

# Freivalds' algorithm for probabilistic verification of matrix multiplication
# See Section 3.3, https://eprint.iacr.org/2021/730.pdf

n = 350
m = 40
l = 500

p = 2**61-1


a = np.random.randint(-2**20, 2**20, (n, m))#.astype(object)
b = np.random.randint(-2**20, 2**20, (m, l))#.astype(object)
c = a @ b

with pzk.PicoZKEMPCompiler('picozk_test'):
    zk_a = pzk.ZKArray.encode(a)
    zk_b = pzk.ZKArray.encode(b)

    # Requires 70,000 multiplication gates
    # zk_c = zk_a @ zk_b

    # Requires 5136 multiplication gates
    new_zk_c = pzk.ZKArray.encode(c)
    u = pzk.ZKArray.encode(np.random.randint(0, p, (1, n)), public=True)
    v = pzk.ZKArray.encode(np.random.randint(0, p, (l, 1)), public=True)

    r1 = u @ zk_a @ zk_b @ v
    r2 = u @ new_zk_c @ v

    pzk.assert0(r1.sum()-r2.sum())
