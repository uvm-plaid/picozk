from picowizpl import *

open_picowizpl('miniwizpl_test')

x = SecretInt(5)
z = x + x
z = z + 1
z = z + SecretInt(10)
print(z)


close_picowizpl()

