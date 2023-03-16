from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test', field=97):
    x = SecretInt(5)
    y = SecretInt(6)

    xb = x.to_binary()
    yb = (-y).to_binary()
    
    eq1 = xb == yb
    assert0(eq1)
    print('x == y?', eq1)

    eq2 = xb == xb
    print('x == x?', eq2)
    assert0(eq2+1)

    eq3 = xb == 6
    print('x == 6?', eq3)
    assert0(eq3)

    eq4 = x < y
    print('x < y?', eq4)
    assert0(eq4)

    eq5 = y < x
    print('y < x?', eq5)
    assert0(eq5 - 1)

    eq6 = y < y
    print('y < y?', eq6)
    assert0(eq6)
