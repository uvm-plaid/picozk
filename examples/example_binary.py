from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    x = SecretInt(5)
    y = SecretInt(6)
    z = SecretInt(6)

    xb = x.to_binary()
    yb = y.to_binary()
    zb = z.to_binary()

    eq1 = xb == yb
    print('x == y?', reveal(eq1), '\n')

    eq2a = xb == xb
    print('x == x?', reveal(eq2a), '\n')

    eq2b = yb == zb
    print('y == z?', reveal(eq2b), '\n')

    eq3 = yb == 6
    print('y == 6?', reveal(eq3), '\n')

    eq4 = x < y
    print('x < y?', reveal(eq4), '\n')

    eq5 = y < x
    print('y < x?', reveal(eq5), '\n')

    eq6 = y < y
    print('y < y?', reveal(eq6), '\n')

    eq7 = x > y
    print('x > y?', reveal(eq7), '\n')

    eq8 = y > x
    print('y > x?', reveal(eq8), '\n')

    eq9 = y > y
    print('y > y?', reveal(eq9), '\n')