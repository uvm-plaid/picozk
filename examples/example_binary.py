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
    # reveal(eq1)

    eq2 = xb == xb
    print('x == x?', reveal(eq2), '\n')
    # reveal(eq2)

    eq2 = yb == zb
    print('y == z?', reveal(eq2), '\n')
    # reveal(eq2)

    eq3 = yb == 6 # y == z, which is correct, but y does not equal 6, which is not right. Discuss proper implementation of creating bints
    print('y == 6?', reveal(eq3), '\n')
    # reveal(eq3)

    eq4 = x < y
    print('x < y?', reveal(eq4), '\n')

    eq5 = y < x
    print('y < x?', reveal(eq5), '\n')

    eq6 = y < y
    print('y < y?', reveal(eq6), '\n')

    eq7 = x > y
    print('x > y?', eq7)
    reveal(eq7)

    eq8 = y > x
    print('y > x?', eq8)
    reveal(eq8)

    eq9 = y > y
    print('y > y?', eq9)
    reveal(eq9)