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
    while not sympy.ntheory.isprime((q - 1) // 2):
        q = sympy.randprime(2 ** lambda_, 2 ** (lambda_ + 1))
    return q

class Commitment:
    def __init__(self, g: int, u: int, S: str):
        self.g = g
        self.u = u
        self.S = S

class Commiter:
    def __init__(self, lambda_: int, t: int):
        self.p1 = generate_safe_prime(lambda_)
        self.p2 = generate_safe_prime(lambda_)
        self.t = t
        self.T = pow(2, t)
        self.N = self.p1 * self.p2
        self.h = random.randint(2, (self.N - 1) // 2)
        while self.h == self.p1 or self.h == self.p2:
            self.h = random.randint(2, (self.N - 1) // 2)
        # LAGRANGE THEOREM STATES THAT THE ORDER OF AN ELEMENT IN A FINITE GROUP DIVIDES THE ORDER OF THE GROUP
        # So, g being an element of QRN, ord(g) divides ord(QRN); ord(g) divides fi(N) // 4
        # That means we don't need to know the order of g as q, we will substitute q for fi(N) // 4
        self.g = pow(self.h, 2, self.N)

    def compute_u(self) -> int:
        a = pow(2, self.T, (self.p1 - 1) * (self.p2 - 1))
        return pow(self.g, a, self.N)

    def compute_W(self) -> list[int]:
        # The commiter must convince the verifier that u = (g ** 2) ** (2 ** t) mod N
        # To do so, the commiter sends a list W containing (g ** 2) ** (2 ** i) mod N for 0 <= i <= t
        # for 1 <= i <= t, the commiter proves that the tuple 
        # (g, W[i-1], W[i]) is a tuple of the form (g, g**x, g**(x**2)) for some x
        # The last element of W equals to u, thus the verifier is assured it was calculated properly
        W = []
        for i in range(self.t + 1):
            a = pow(2, 2 ** i, (self.p1 - 1) * (self.p2 - 1))
            val = pow(self.g, a, self.N)
            W.append(val)
        return W
    
    def commit(self, message: str):
        # here we expect the message to only contain 0s and 1s
        for ch in set(message):
            if ch != '0' and ch != '1':
                raise ValueError("Expected message to contain only 0s and 1s")
        S = []
        l = len(message)
        for i in range(1, l + 1):
            a = pow(2, (2 ** self.t - i), (self.p1 - 1) * (self.p2 - 1))
            rez = pow(self.g, a, self.N) & 1 # get lsb of succesive square roots of u modulo N
            S.append(str(rez ^ int(message[i - 1])))
        S = "".join(S)
        return Commitment(self.g, self.compute_u(), S)
    
class Verifier:
    def __init__(self, N: int, t: int, R: int):
        self.N = N
        self.t = t
        self.R = R

    def commit_to_cs(self):
        Cs = []
        self.pp = PedersenCommitmentPublicParams()
        for i in range(0, self.t):
            c = random.randint(0, self.R)
            commitment, opening = pedersen_commit(c, self.pp)
            Cs.append((c, commitment, opening))
        self.Cs = Cs

    def open(self, C: Commitment, v: int):
        l = len(C.S)
        if pow(v, 2 ** l, self.N) != C.u:
            raise ValueError("Recieved v does not equal to expected value")
        msg = []
        for i in range(1, l + 1):
            val = pow(v, 2 ** (l - i), self.N) & 1
            msg.append(str(val ^ (int(C.S[i - 1]))))
        return "".join(msg)

    def force_open(self, C: Commitment):
        start = time.time()
        print("Started force opening")
        l = len(C.S)
        a = pow(2, 2 ** self.t - l)
        v = pow(C.g, a, self.N)
        # In this case, the verifier needs to get v by himself computing v = g ** (2 ** (2 ** t - l))
        # The time lock puzzle consists of (2 ** t - l) squarings of g mod N
        msg = []
        for i in range(1, l + 1):
            val = pow(v, 2 ** (l - i), self.N) & 1
            msg.append(str(val ^ (int(C.S[i - 1]))))
        print(f"Finished force opening for commitment in {time.time() - start} seconds")
        return "".join(msg)

if __name__ == '__main__':
    lambda_ = 64
    t = 24
    msg = "01010111"
    subcontractor = Commiter(lambda_, t)
    commitment = subcontractor.commit(msg)
    a = pow(2, (2 ** t - len(msg)), (subcontractor.p1 - 1) * (subcontractor.p2 - 1))
    v = pow(subcontractor.g, a, subcontractor.N)
    orange = Verifier(subcontractor.N, t, 128)
    orange.commit_to_cs()
    # for (c, comm_c, open_c) in orange.Cs:
    #     print(f"{c} opens up: {pedersen_open(comm_c, c, open_c, orange.pp)}")
    print(orange.open(commitment, v))
    print(orange.force_open(commitment))
