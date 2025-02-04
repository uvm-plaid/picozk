from picozk import *

with PicoZKCompiler('picozk_test', field=97):
    x = SecretInt(-5)
    y = SecretInt(6)

    xb = x.to_binary()
    yb = (-y).to_binary()
    print("Completed to_binary on x and y")

    eq1 = xb == yb
    print("Through equality")
    print('x == y?', eq1)
    reveal(eq1)  # Breaks here.

    eq2 = xb == xb
    print('x == x?', reveal(eq2))
    # reveal(eq2)

    eq3 = xb == 6
    print('x == 6?', reveal(eq3))
    # reveal(eq3)

    eq4 = x < y
    print('x < y?', eq4)
    reveal(eq4)

    eq5 = y < x
    print('y < x?', eq5)
    reveal(eq5)

    eq6 = y < y
    print('y < y?', eq6)
    reveal(eq6)

    eq7 = x > y
    print('x > y?', eq7)
    reveal(eq7)

    eq8 = y > x
    print('y > x?', eq8)
    reveal(eq8)

    eq9 = y > y
    print('y > y?', eq9)
    reveal(eq9)