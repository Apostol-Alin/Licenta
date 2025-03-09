import random
import sympy
from sympy.ntheory import isprime

class PedersenCommitmentPublicParams:
    def __init__(self, lambda_: int):
        lambda_ = 20 # Problem for big value for security parameter...
        # De discutat despre grupul si subgrupul peste care lucreaza Perdersen Commitment Scheme
        p = sympy.randprime(2 ** lambda_, 2 ** (lambda_ + 1)) # security parameter lambda
        c = 1
        q = p * c + 1
        while not isprime(q):
            c += 1
            q = p * c + 1

        for x in range(2, q):
            x_ = pow(x, q, p)
            if x_ == 1:
                break
        PedersenCommitmentPublicParams.g = x
        
        exp = random.randint(2, q - 1)
        PedersenCommitmentPublicParams.h = pow(PedersenCommitmentPublicParams.g, exp, q) # we compute h = g ^ exp mod q where exp is chosen randomly so we do not know log(h) in regard to g (discrete logarithm problem)
        PedersenCommitmentPublicParams.q = q

def pedersen_commit(message: int) -> tuple[int, int]:
    alpha = int(random.randint(1, PedersenCommitmentPublicParams.q - 1))
    commitment = (pow(PedersenCommitmentPublicParams.g, message, PedersenCommitmentPublicParams.q) * pow(PedersenCommitmentPublicParams.h, alpha, PedersenCommitmentPublicParams.q)) % PedersenCommitmentPublicParams.q
    return commitment, alpha

def pedersen_open(commitment: int, message: int, opening: int) -> bool:
    return commitment == (pow(PedersenCommitmentPublicParams.g, message, PedersenCommitmentPublicParams.q) * pow(PedersenCommitmentPublicParams.h, opening, PedersenCommitmentPublicParams.q)) % PedersenCommitmentPublicParams.q