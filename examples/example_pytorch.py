import torch
from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    t = torch.rand((10, 5))
    print(t)
    t = t.apply_(lambda x: SecretInt(x))
    print(t)
