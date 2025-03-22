import sympy
from sympy.ntheory import isprime
import numpy as np
import random
import math

class RSAG:
    def __init__(self, lambda_, t):
        # security parameter
        self.lambda_ = lambda_
        self.t = t
        self.set_N()
        self.generate_RSAGroup()
    def generate_safe_prime(self):
        print("Generating safe prime...")
        # We define a safe prime a prime number `q` for which (q - 1) // 2 is also prime
        q = sympy.randprime(2 ** self.lambda_, 2 ** (self.lambda_ + 1))
        while not isprime((q - 1) // 2):
            q = sympy.randprime(2 ** self.lambda_, 2 ** (self.lambda_ + 1))
        return q
    def set_N(self):
        q1 = self.generate_safe_prime()
        q2 = self.generate_safe_prime()
        self.q1 = q1
        self.q2 = q2
        self.N = q1 * q2
    def generate_RSAGroup(self):
        print("Generating generators...")
        while True:
            x = random.randint(2, self.N)
            if math.gcd(x, self.N) == 1:
                g = pow(x, 2, self.N)
                if g != 1:
                    break

        while True:
            x = random.randint(2, self.N)
            if math.gcd(x, self.N) == 1:
                h = pow(x, 2, self.N)
                if h != 1 and h != g:
                    break

        self.g = g
        self.h = h

