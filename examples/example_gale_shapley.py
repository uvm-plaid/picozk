from picozk import *
import numpy as np

NO_MARRIAGE = 100000

#NUM_INDIVIDUALS = 35000
NUM_INDIVIDUALS = 100
NUM_PREFS = 15

# iterations <= n^2
#ITERS = NUM_INDIVIDUALS**2
ITERS = 100

# men are 0..n, women are n..2n
men = list(range(NUM_INDIVIDUALS))
women = list(range(NUM_INDIVIDUALS, 2*NUM_INDIVIDUALS))

men_prefs = np.asarray([np.random.permutation(women) for _ in men])
women_prefs = np.asarray([np.random.permutation(men) for _ in women])
prefs = np.vstack([men_prefs, women_prefs])

def index(mat, val, start, length):
    assert isinstance(length, int)
    result = -1
    for offset in range(length):
        result = mux(mat[start + offset] == val, start + offset, result)
    return result

def prefers(w, m, m_p):
    v_m   = index(preference_matrix, m,   w*NUM_PREFS, NUM_PREFS)
    v_m_p = index(preference_matrix, m_p, w*NUM_PREFS, NUM_PREFS)
    return v_m < v_m_p

def gale_shapley(preference_matrix):
    unmarried_men = ZKStack(len(men))
    for x in men:
        unmarried_men.push(SecretInt(x))

    marriages = ZKList([NO_MARRIAGE for _ in women])
    next_proposal = ZKList([0 for _ in men])

    for i in range(ITERS):
        if i == ITERS-1:
            penultimate_marriages = [marriages[i] for i in range(len(marriages))]

        m = unmarried_men.pop()
        w = preference_matrix[m*NUM_PREFS + next_proposal[m]]
        next_proposal[m] += 1

        wi = w-len(men)

        # branch 1
        b1 = marriages[wi] == NO_MARRIAGE
        v = mux(b1, m, marriages[wi])
        marriages[wi] = v

        # branch 2
        b2 = prefers(w, m, marriages[wi])
        b22 = b2 & (~ b1)
        unmarried_men.cond_push(b22, marriages[wi])
        marriages[wi] = mux(b22, m, marriages[wi])

        # branch 3 (else)
        b3 = (~ b1) & (~ b2)
        unmarried_men.cond_push(b3, m)

    reached_fixpoint = 1
    for i in range(len(marriages)):
        reached_fixpoint = (marriages[i] == penultimate_marriages[i]) & reached_fixpoint
    return marriages, reached_fixpoint

with PicoZKCompiler('picozk_test', options=['ram']):
    preference_matrix = ZKList(list(prefs.flatten()))
    final_marriages, fp = gale_shapley(preference_matrix)
    print(fp)

    # reveal the final marriages
    for i in range(len(final_marriages)):
        reveal(final_marriages[i])

    # check that we did enough iterations
    assert0(~fp)
