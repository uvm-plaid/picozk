from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test', options=['ram']):
    x = SecretStack(5)
    for i in range(3):
        x.push(i)

    for i in range(3):
        z = x.pop()
        reveal(z)

    for i in range(3):
        x.push(i)

    a = SecretInt(2)
    for i in range(3):
        z = x.cond_pop(a == i)
        reveal(z)

    for i in range(3):
        x.cond_push(a == i, i)

    for i in range(3):
        z = x.pop()
        reveal(z)
