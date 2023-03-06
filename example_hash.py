from picowizpl import *
import galois

with PicoWizPLCompiler('miniwizpl_test'):
    p = 2**31-1
    gf = galois.GF(p)
    n = 100
    input_vec = [1,2,3,4]
    input_vec = [SecretInt(gf(v)) for v in input_vec]

    rvec = np.random.randint(0, p, (len(input_vec), len(input_vec)))

    state = input_vec
    for _ in range(n):
        state = np.dot(rvec, state)

    print(state)
