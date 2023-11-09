import picozk as pzk
import numpy as np

with pzk.PicoZKEMPCompiler('picozk_test'):
    x = pzk.SecretInt(5)
    z = x
    for _ in range(20):
        z = z + x * x
    pzk.reveal(z)

    # for _ in range(10):
    #     x = np.random.randint(0, 100, (200, 100))
    #     y = np.random.randint(0, 100, (100, 50))
    #     xz = pzk.ZKArray.encode(x)
    #     yz = pzk.ZKArray.encode(y)
    #     zz = xz @ yz
    #     total = zz.sum()
    #     pzk.reveal(total)

