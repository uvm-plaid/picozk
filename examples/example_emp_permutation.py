import picozk as pzk
import numpy as np
import galois

p = 2**61-1

n = 1000000
m = 10

a = np.random.randint(0, 1000, (n, m))

with pzk.PicoZKEMPCompiler('picozk_test'):
    zk_a = pzk.ZKArray.encode(a)

    a_sorted = a[a[:, 1].argsort()]
    zk_a_sorted = pzk.ZKArray.encode(a_sorted)

    rs = np.random.randint(1, p, (m, 1))
    zk_rs = pzk.ZKArray.encode(rs)

    total_1 = (zk_a @ zk_rs).prod()
    total_2 = (zk_a_sorted @ zk_rs).prod()

    pzk.assert0(total_1 - total_2)
