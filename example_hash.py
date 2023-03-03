from picowizpl import *

open_picowizpl('miniwizpl_test')

n = 100
input_vec = [1,2,3,4]
input_vec = [SecretInt(v) for v in input_vec]
p = 97
np.random.seed(1)

rvec = np.random.randint(0, p, (len(input_vec), len(input_vec)))

state = input_vec
for _ in range(n):
    state = np.dot(rvec, state)

print(state)

close_picowizpl()
