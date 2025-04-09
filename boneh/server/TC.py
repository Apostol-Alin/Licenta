import sympy
import sympy.ntheory
from PedersenCommitmentScheme import *
import random
import time

def generate_safe_prime(lambda_: int) -> int:
    q = sympy.randprime(2 ** lambda_, 2 ** (lambda_ + 1))
    while not q % 4 == 3:
        q = sympy.randprime(2 ** lambda_, 2 ** (lambda_ + 1))
    return q

class Commitment:
    def __init__(self, g: int, u: int, S: str):
        self.g = g
        self.u = u
        self.S = S

class Commiter:
    def __init__(self, lambda_: int, t: int, B: int = 128):
        self.p1 = generate_safe_prime(lambda_)
        self.p2 = generate_safe_prime(lambda_)
        self.t = t
        self.T = pow(2, t)
        self.N = self.p1 * self.p2
        self.h = random.randint(2, self.N - 1)
        self.B = B
        while self.h == self.p1 or self.h == self.p2:
            self.h = random.randint(2, self.N - 1)
        prime_less_than_B = [pow(x, self.N, self.N) for x in range(2, self.B) if sympy.ntheory.isprime(x)]
        prod = 1
        for x in prime_less_than_B:
            prod *= x
        self.g = pow(self.h, prod, self.N)

    def compute_u(self) -> int:
        a = pow(2, self.T, (self.p1 - 1) * (self.p2 - 1))
        return pow(self.g, a, self.N)

    def compute_W(self):
        # The commiter must convince the verifier that u = (g ** 2) ** (2 ** t) mod N
        # To do so, the commiter sends a list W containing (g ** 2) ** (2 ** i) mod N for 0 <= i <= t
        # for 1 <= i <= t, the commiter proves that the tuple 
        # (g, W[i-1], W[i]) is a tuple of the form (g, g**x, g**(x**2)) for some x
        # The last element of W equals to u, thus the verifier is assured it was calculated properly
        self.W = []
        for i in range(self.t + 1):
            a = pow(2, 2 ** i, (self.p1 - 1) * (self.p2 - 1))
            val = pow(self.g, a, self.N)
            self.W.append(val)
    
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
    
    def compute_pairs(self):
        if len(self.W) != self.t + 1:
            raise ValueError(f"Expected W to have {self.t + 1} elements, but found {len(self.W)}")
        self.alphas = []
        self.pairs = []
        for i in range(self.t):
            alpha = random.randint(1, (self.p1 - 1) * (self.p2 - 1))
            self.alphas.append(alpha)
            z = pow(self.g, alpha, self.N)
            w = pow(self.W[i], alpha, self.N)
            self.pairs.append([z, w])
        
    def compute_Ys(self, Cs: list[int]):
        if len(Cs) != self.t:
            raise ValueError(f"Expected Cs to have {self.t} elements, but found {len(Cs)}")
        self.Ys = []
        for i in range(self.t):
            alpha = self.alphas[i]
            a = pow(2, 2 ** i)
            Y = ((Cs[i] * a) % ((self.p1 - 1) * (self.p2 - 1)) + alpha) % ((self.p1 - 1) * (self.p2 - 1))
            self.Ys.append(Y)

    
class Verifier:
    def __init__(self, N: int, t: int, R: int, B: int = 128):
        self.N = N
        self.t = t
        self.R = R
        self.B = B

    def commit_to_cs(self):
        Cs = []
        self.pp = PedersenCommitmentPublicParams()
        for i in range(0, self.t):
            c = random.randint(0, self.R)
            commitment, opening = pedersen_commit(c, self.pp)
            Cs.append((c, commitment, opening))
        self.Cs = Cs

    def open(self, C: Commitment, v_prime: int):
        l = len(C.S)
        prime_less_than_B = [pow(x, self.N, self.N) for x in range(2, self.B) if sympy.ntheory.isprime(x)]
        prod = 1
        for x in prime_less_than_B:
            prod *= x
        v = pow(v_prime, prod, self.N)
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
    
    def check_validity(self, W: list[int], pairs: list[list[int]], Ys: list[int], g: int):
        if len(pairs) != self.t or len(Ys) != self.t:
            raise ValueError(f"Expected pairs and Ys to have {self.t} elements, but found {len(pairs)} and {len(Ys)}")
        if len(W) != self.t + 1:
            raise ValueError(f"Expected W to have {self.t + 1} elements, but found {len(W)}")
        for i in range(1, self.t + 1):
            z, w = pairs[i - 1]
            y = Ys[i - 1]
            check1 = pow(g, y, self.N) * pow(W[i - 1], -self.Cs[i - 1][0], self.N) % self.N
            check2 = pow(W[i - 1], y, self.N) * pow(W[i], -self.Cs[i - 1][0], self.N) % self.N
            if check1 != z or check2 != w:
                return False
        return True

if __name__ == '__main__':
    lambda_ = 128
    t = 22
    msg = "01010111"
    subcontractor = Commiter(lambda_, t)
    commitment = subcontractor.commit(msg)
    a = pow(2, (2 ** t - len(msg)), (subcontractor.p1 - 1) * (subcontractor.p2 - 1))
    v = pow(subcontractor.h, a, subcontractor.N)
    subcontractor.compute_W()
    orange = Verifier(subcontractor.N, t, 128)
    validity = 0
    for _ in range(10):
        orange.commit_to_cs()
        subcontractor.compute_pairs()
        subcontractor.compute_Ys([c for (c, _, _) in orange.Cs])
        # for (c, comm_c, open_c) in orange.Cs:
        #     print(f"{c} opens up: {pedersen_open(comm_c, c, open_c, orange.pp)}")
        if orange.check_validity(subcontractor.W, subcontractor.pairs, subcontractor.Ys, subcontractor.g):
            validity += 1
    if validity == 10:
        print(orange.open(commitment, v))
        print(orange.force_open(commitment))
