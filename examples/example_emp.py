import picozk as pzk
import numpy as np

with pzk.PicoZKEMPCompiler('picozk_test'):
    # x = pzk.SecretInt(5)
    # z = x
    # for _ in range(20):
    #     z = z + x * x
    # pzk.reveal(z)

    x = np.random.randint(0, 100, 20000000)
    xz = pzk.ZKArray(x)
    print(xz)
    total = xz.sum()
    print(total)
    pzk.reveal(total)
