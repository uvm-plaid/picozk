import os
import glob
tests = glob.glob('example*.py')

for test in tests:
    print('==================================================')
    print(f'Running test: {test}')
    if os.path.exists('picozk_test.rel'):
        os.system('rm picozk_test.*')
    os.system(f'python {test}')
    if os.path.exists('picozk_test.rel'):
        os.system('wtk-firealarm picozk_test.*')
    if os.path.exists('picozk_test.rel'):
        os.system('rm picozk_test.*')
