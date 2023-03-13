import os
import glob
tests = glob.glob('example*.py')

for test in tests:
    print('==================================================')
    print(f'Running test: {test}')
    if os.path.exists('miniwizpl_test.rel'):
        os.system('rm miniwizpl_test.*')
    os.system(f'python {test}')
    if os.path.exists('miniwizpl_test.rel'):
        os.system('wtk-firealarm miniwizpl_test.*')
