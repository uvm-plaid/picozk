# PicoZK

Integrated, Efficient, and Extensible Zero-Knowledge Proof Engineering

----

## Installation

Clone the repository and then install with `pip install`:

```
git clone git@github.com:uvm-plaid/picozk.git
cd picozk
pip install .
```

If you want to run the [examples](examples), you'll need to install
some extra python libraries. These can be done by running `pip install
.[examples]`.


## Usage

To generate a zero-knowledge (ZK) statement, write a Python program
that uses the PicoZK library, and then run the program to generate the
statement. For example, the following program corresponds to a ZK
statement that the prover knows a number `x` such that `x + x * x` is
30:

``` python
from picozk import *

with PicoZKCompiler('picozk_test'):
    x = SecretInt(5)
    z = x + x * x
    assert0(z + -30)
```

Running this program results in three files:
- `picozk_test.rel`: the *relation*, which is the statement itself
  (known to both prover and verifier)
- `picozk_test.type0.ins`: the *instance*, which holds public
  information (known to both prover and verifier, always empty in our
  setting)
- `picozk_test.type0.wit`: the *witness*, which holds secret
  information (known only to prover)

These files can be used to generate a ZK proof using any backend
compatible with the [SIEVE intermediate representation
(IR)](https://stealthsoftwareinc.github.io/wizkit-blog/2021/09/20/introducing-the-sieve-ir.html) -
for example, the [EMP Toolkit](https://github.com/emp-toolkit/emp-ir).
