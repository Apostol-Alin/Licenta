import random
import sympy
from sympy.ntheory import isprime
import ecdsa

class PedersenCommitmentPublicParams:
    def __init__(self, lambda_: int):
        curve = ecdsa.SECP256k1
        PedersenCommitmentPublicParams.g = curve.generator
        PedersenCommitmentPublicParams.N = curve.order
        PedersenCommitmentPublicParams.h = random.randint(2, self.N - 1) * self.g # we do not know log(h) in regard to g
        print(PedersenCommitmentPublicParams.N)

def pedersen_commit(message: int) -> tuple[int, int]:
    alpha = int(random.randint(1, PedersenCommitmentPublicParams.N - 1))
    commitment = (message * PedersenCommitmentPublicParams.g)  +\
            (alpha * PedersenCommitmentPublicParams.h) 
    return commitment, alpha

def pedersen_open(commitment: int, message: int, opening: int) -> bool:
    return commitment == \
            message * PedersenCommitmentPublicParams.g +\
            opening * PedersenCommitmentPublicParams.h