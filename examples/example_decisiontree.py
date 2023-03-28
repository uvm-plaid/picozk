from picozk import *

import numpy as np
from sklearn import svm, datasets, neighbors, tree

from dataclasses import dataclass

iris = datasets.load_iris()
X = iris.data#[:, :2]
y = iris.target
bc = datasets.load_breast_cancer()
X = bc.data#[:, :2]
y = bc.target

dt = tree.DecisionTreeClassifier(max_depth = None)
dt = tree.DecisionTreeClassifier()
dt.fit(X, y)

SCALE = 10000

class Tree:
    pass

@dataclass
class Node(Tree):
    feature: int
    threshold: int
    left: Tree
    right: Tree

    def depth(self):
        return max(self.left.depth(), self.right.depth()) + 1
    def size(self):
        return 4 + self.left.size() + self.right.size()

@dataclass
class Leaf(Tree):
    label: int

    def depth(self):
        return 0
    def size(self):
        return 4

def export_tree(tree, node, depth):
    class_name = np.argmax(tree.value[node][0])

    if tree.feature[node] != -2:
        # node
        lhs = export_tree(tree, tree.children_left[node], depth + 1)
        rhs = export_tree(tree, tree.children_right[node], depth + 1)
        thresh = int(tree.threshold[node]*SCALE)
        return Node(tree.feature[node], thresh, lhs, rhs)
    else:
        # leaf
        return Leaf(class_name)
        #return (' ' * depth) + f'(leaf {class_name})'

@dataclass
class SecretTree:
    ptr: int
    ram: ZKRAM

    def get_branch(self, cond):
        left_ptr = self.ram.read(self.ptr+2)
        right_ptr = self.ram.read(self.ptr+3)
        branch_ptr = mux(cond, left_ptr, right_ptr)
        return SecretTree(branch_ptr, self.ram)

    def get_data(self):
        return self.ram.read(self.ptr), self.ram.read(self.ptr+1)

def encode_tree(t: Tree):
    ram_size = t.size()
    ram = ZKRAM(ram_size)
    free_ptr = 0

    def encode(t: Tree):
        nonlocal free_ptr
        if isinstance(t, Leaf):
            ptr = free_ptr
            ram.write(free_ptr, int(t.label))
            free_ptr += 4
            return ptr
        else:
            left_ptr = encode(t.left)
            right_ptr = encode(t.right)
            ptr = free_ptr
            ram.write(free_ptr, int(t.feature))
            ram.write(free_ptr+1, int(t.threshold))
            ram.write(free_ptr+2, left_ptr)
            ram.write(free_ptr+3, right_ptr)
            free_ptr += 4
            return ptr

    root_ptr = encode(t)
    return SecretTree(root_ptr, ram)



t = export_tree(dt.tree_, 0, 0)

def classify(x, t):
    if isinstance(t, Leaf):
        return t.label
    else:
        if int(x[t.feature]*SCALE) < t.threshold:
            return classify(x, t.left)
        else:
            return classify(x, t.right)

results = [classify(x, t) for x in X]

with PicoZKCompiler('picozk_test', options=['ram']):
    st = encode_tree(t)

    # print(st)
    # for i, v in enumerate(st.ram.val):
    #     print(i, ':', v)

    def classify_st(x, lst, d):
        if d == 0:
            label, _ = lst.get_data()
            return label
        else:
            feature, threshold = lst.get_data()
            cond = x[feature] < threshold
            next_st = lst.get_branch(cond)
            return classify_st(x, next_st, d-1)

    for i, x_i in enumerate(X):
        xx = ZKList([int(x * SCALE) for x in x_i])
        result = classify_st(xx, st, 8)

        reveal(result)

        # to test against the actual decision tree
        # difference = result - int(results[0])
        # assert0(difference)


#print(t)
print('t depth:', t.depth())


print('dataset shape:', X.shape)
print('score:', dt.score(X, y))
print('num correct:', dt.score(X, y) * len(X))
print('depth:', dt.tree_.max_depth)
print('number of nodes:', len(dt.tree_.feature))
#print(X)

def classify(x, t):
    if isinstance(t, Leaf):
        return t.label
    else:
        if int(x[t.feature]*SCALE) < t.threshold:
            return classify(x, t.left)
        else:
            return classify(x, t.right)

results = [classify(x, t) for x in X]
correct = y == results
print(np.sum(correct))
