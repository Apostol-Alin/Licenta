import random
import ecdsa
import ecdsa.ecdsa
import ecdsa.ellipticcurve

class PedersenCommitmentPublicParams:
    def __init__(self):
        curve = ecdsa.SECP256k1
        self.g = curve.generator
        self.N = curve.order
        self.h = random.randint(2, self.N - 1) * self.g # we do not know log(h) in regard to g

def pedersen_commit(message: int, pp: PedersenCommitmentPublicParams) -> tuple[int, int]:
    alpha = int(random.randint(1, pp.N - 1))
    commitment = (message * pp.g)  +\
            (alpha * pp.h) 
    return commitment, alpha

def pedersen_open(commitment: int, message: int, opening: int, pp: PedersenCommitmentPublicParams) -> bool:
    return commitment == \
            message * pp.g +\
            opening * pp.h
