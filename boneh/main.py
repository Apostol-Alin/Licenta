import sympy
import sympy.ntheory
from PedersenCommitmentScheme import *
import random
import time

def generate_random_prime(lambda_: int) -> int:
    p = sympy.randprime(2 ^ (lambda_ - 1), 2 ^ lambda_)
    while p % 4 != 3:
        p = sympy.randprime(2 ^ (lambda_ - 1), 2 ^ lambda_)
    return p

def generate_safe_prime(lambda_: int) -> int:
    print("Generating safe prime...")
    # We define a safe prime a prime number `q` for which (q - 1) // 2 is also prime
    q = sympy.randprime(2 ** lambda_, 2 ** (lambda_ + 1))
    while not isprime((q - 1) // 2):
        q = sympy.randprime(2 ** lambda_, 2 ** (lambda_ + 1))
    return q

def open(h,g,u,comm,v, N):
    l = len(comm)
    if pow(v, 2 ** l, N) != u:
        raise ValueError("Recieved v does not equal to expected value")
    msg = []
    for i in range(1, l + 1):
        val = pow(v, 2 ** (l - i), N) & 1
        msg.append(str(val ^ (int(comm[i - 1]))))
    return "".join(msg)

def force_open(h,g,u,comm,N,t):
    start = time.time()
    print("Started force opening")
    l = len(comm)
    a = pow(2, 2 ** t - l)
    v = pow(g, a, N)
    msg = []
    for i in range(1, l + 1):
        val = pow(v, 2 ** (l - i), N) & 1
        msg.append(str(val ^ (int(comm[i - 1]))))
    print(f"Finished force opening for commitment in {time.time() - start} seconds")
    return "".join(msg)

class Commiter:
    def __init__(self, lambda_: int, t: int):
        self.p1 = generate_safe_prime(lambda_)
        self.p2 = generate_safe_prime(lambda_)
        self.t = t
        self.T = pow(2, t)
        self.N = self.p1 * self.p2
        self.h = random.randint(2, self.N - 1)
        while self.h == self.p1 or self.h == self.p2:
            self.h = random.randint(2, self.N - 1)
        self.g = pow(self.h, 2, self.N)

    def calculate_u(self) -> int:
        a = pow(2, self.T, (self.p1 - 1) * (self.p2 - 1))
        return pow(self.g, a, self.N)
    
    def commit(self, message: str):
        # here we expect the message to only contain 0s and 1s
        commitment = []
        l = len(message)
        for i in range(1, l + 1):
            a = pow(2, (2 ** self.t - i), (self.p1 - 1) * (self.p2 - 1))
            rez = pow(self.g, a, self.N) & 1 # get lsb of succesive square roots of u modulo N
            commitment.append(str(rez ^ int(message[i - 1])))
        return "".join(commitment)

if __name__ == '__main__':
    lambda_ = 64
    t = 27
    msg = "01010111"
    subcontractor = Commiter(lambda_, t)
    commitment = subcontractor.commit(msg)
    a = pow(2, (2 ** t - len(msg)), (subcontractor.p1 - 1) * (subcontractor.p2 - 1))
    v = pow(subcontractor.g, a, subcontractor.N)
    print(open(subcontractor.h, subcontractor.g, subcontractor.calculate_u(), commitment, v, subcontractor.N))
    print(force_open(subcontractor.h, subcontractor.g, subcontractor.calculate_u(), commitment, subcontractor.N, t))