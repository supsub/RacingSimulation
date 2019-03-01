import random

import numpy as np


class Network(object):

    def __init__(self, sizes):
        self.mutation_chance = 0.02
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]

    def feed_forward(self, a):
        """Return the output of the network if "a" is input."""
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a) + b)
        return a
    def set_biases(self,nets):
        for x in range(len(self.biases)):
            for y in range(len(self.biases[x])):
                self.biases[x][y] = nets[random.randrange(0, len(nets))].biases[x][y]
                self.mutate_biases(x, y)
    def set_weights(self,nets):
        for x in range(len(self.weights)):
            for y in range(len(self.weights[x])):
                for z in range (len(self.weights[x][y])):
                    self.weights[x][y][z] = nets[random.randrange(0, len(nets))].weights[x][y][z]
                    self.mutate_weights(x, y,z)
    def mutate_biases(self, x, y):
        if random.random() < self.mutation_chance:
            self.biases[x][y] = np.random.randn()

    def mutate_weights(self, x, y, z):
        if random.random() < self.mutation_chance:
            self.weights[x][y][z] = np.random.randn()

def sigmoid(z):
    """The sigmoid function."""
    return 1.0 / (1.0 + np.exp(-z))

