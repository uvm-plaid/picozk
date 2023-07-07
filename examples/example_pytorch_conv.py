from picozk import *
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

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


class Classifier(nn.Module):
    def __init__(self):
        super(Classifier, self).__init__()
        self.network = nn.Sequential(
            torch.nn.Conv2d(1, 16, 8, 2, bias=False),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2, 1), 
            torch.nn.Conv2d(16, 32, 4, 2, bias=False),
            torch.nn.ReLU(), 
            torch.nn.MaxPool2d(2, 1), 
            torch.nn.Flatten(), 
            torch.nn.Linear(288, 32, bias=False),
            torch.nn.ReLU(), 
            torch.nn.Linear(32, 10, bias=False))
    def forward(self, x):
        return self.network(x)

model = Classifier()
model.eval()
test_input = torch.randn(1, 28, 28)
print(model(test_input))
