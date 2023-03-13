import sys
from picowizpl import *

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = 'run_tests.py'

# the accept state is 1000000
accept_state = 1000000

# a Python function to create a dfa from a string
# we assume a default transition back to 0
def dfa_from_string(text):
    next_state = {}
    alphabet = set(text)

    for i in range(len(text)):
        for j in alphabet:
            if j == text[i]:
                if i == len(text) - 1:
                    # accept state
                    next_state[(i, ord(j))] = accept_state
                else:
                    next_state[(i, ord(j))] = i+1
            else:
                for k in range(len(text)):
                    try:
                        if text.index(text[k:i] + j) == 0 and k <= i:
                            next_state[(i, ord(j))] = len(text[k:i] + j)
                            break
                    except ValueError:
                        pass
    return next_state

# read the target file & convert to secret string
with open(filename, 'r') as f:
    file_data = f.read()

with PicoWizPLCompiler('miniwizpl_test'):
    file_string = [SecretInt(ord(c)) for c in file_data]
    dfa = dfa_from_string('import')

    def next_state(char, state):
        output = 0

        for (dfa_state, dfa_char), next_state in dfa.items():
            output = mux((state == dfa_state) & (char == dfa_char),
                         next_state,
                         output)

        output = mux(state == accept_state, accept_state, output)
        return output

    state = 0
    for c in file_string:
        state = next_state(c, state)

    print('dfa:', dfa)
    print('target string:', [ord(c) for c in "import"])
    print('final state:', state)
    assert0(~(state == val_of(state)))
