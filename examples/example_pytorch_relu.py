from picowizpl import *
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

SCALE = 10000
p = 2**61-1

def encode(x):
    return int(SCALE*x) % p

encode_matrix = np.vectorize(encode)
encode_zk_matrix = np.vectorize(lambda x: SecretInt(encode(x)), otypes=[Wire])

zk = False

class ZKLinear(torch.nn.Linear):
    def forward(self, inp):
        if zk:
            if not self.training and not hasattr(self, 'zk_weights'):
                self.zk_weight = encode_zk_matrix(self.weight.detach().numpy())
                self.zk_bias = encode_zk_matrix(self.bias.detach().numpy())

            return inp @ self.zk_weight.T + self.zk_bias * self.bias_scale
        else:
            return super().forward(inp)

class ZKReLU(torch.nn.ReLU):
    def forward(self, inp):
        if zk:
            is_pos = np.vectorize(lambda x: (~x.is_negative()).to_arith(),
                                  otypes=[ArithmeticWire])
            return is_pos(inp) * inp
        else:
            return super().forward(inp)

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = ZKLinear(784, 32)
        self.fc1.bias_scale = SCALE
        self.fc2 = ZKLinear(32, 10)
        self.fc2.bias_scale = SCALE**2
        self.relu = ZKReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

with PicoWizPLCompiler('miniwizpl_test'):
    model = Net()
    model.eval()

    test_input = torch.randn(10, 784)
    encoded_input = encode_matrix(test_input.detach().numpy())
    output1 = model(test_input)
    #print(output1)
    zk=True
    output = model(encoded_input)

    for output_probs in output:
        for x in output_probs:
            reveal(x)

    #print(output_probs)
    #print(output1)
