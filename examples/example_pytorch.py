from picowizpl import *
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(784, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 10)

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x

model = Net()
model.eval()

test_input = torch.randn(10, 784)
output = model(test_input)
#print(output)

SCALE = 1000
p = 2**61-1

def encode(x):
    return int(SCALE*x) % p

encode_matrix = np.vectorize(encode)
encode_zk_matrix = np.vectorize(lambda x: SecretInt(encode(x)), otypes=[Wire])

@dataclass
class ZKTensor:
    val: any

model_weights = {}

old_linear = F.linear
def my_linear(inp, weight, bias):
    if weight in model_weights or bias in model_weights:
        assert weight in model_weights and bias in model_weights
        A = model_weights[weight].val.T
        b = model_weights[bias].val
        if isinstance(inp, torch.Tensor):
            # this is a regular input, need to encode it
            input_mat = inp.detach().numpy()
            encoded_input = encode_matrix(input_mat)
        elif isinstance(inp, ZKTensor):
            # this is already encoded
            encoded_input = inp.val
        else:
            raise Exception('unknown input:', inp)
        result = (encoded_input @ A) + b
        return ZKTensor(result)
    else:
        return old_linear(inp, weight, bias)
F.linear = my_linear

with PicoWizPLCompiler('miniwizpl_test'):
    # encode the model
    for param in model.parameters():
        old_data = param.data.detach().numpy()
        new_data = ZKTensor(encode_zk_matrix(old_data))
        model_weights[param] = new_data

    output = model(test_input)
    assert isinstance(output, ZKTensor)
    for output_probs in output.val:
        for x in output_probs:
            reveal(x)
