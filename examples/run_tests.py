import glob
import os
import subprocess
import sys

tests = glob.glob('example*.py')

for test in tests:
    print('==================================================')
    print(f'Running test: {test}')
    if os.path.exists('picozk_test.rel'):
        subprocess.run(['rm', '-f'] + glob.glob('picozk_test.*'), check=True)
    try:
        subprocess.run(['python3', f'{test}'], check=True)
    except subprocess.CalledProcessError as err:
        print(f'error in python file for {test}')
        sys.exit(err.returncode);
    if os.path.exists('picozk_test.rel'):
        try:
            subprocess.run(['wtk-firealarm'] + glob.glob('picozk_test.*'), check=True)
        except subprocess.CalledProcessError as err:
            print(f'invalid input for {test}')
            sys.exit(err.returncode);
    if os.path.exists('picozk_test.rel'):
        subprocess.run(['rm', '-f'] + glob.glob('picozk_test.*'), check=True)
sys.exit(0)
