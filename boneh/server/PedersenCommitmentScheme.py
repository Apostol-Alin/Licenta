import ecdsa
import secrets

class PedersenCommitmentPublicParams:
    def __init__(self):
        curve = ecdsa.SECP256k1
        self.g = curve.generator
        self.N = curve.order
        random_power = secrets.randbelow(self.N - 1)
        while random_power <= 2:
            random_power = secrets.randbelow(self.N - 1)
        self.h = self.g * random_power  # we do not know log(h) in regard to g

def pedersen_commit(message: int, pp: PedersenCommitmentPublicParams) -> tuple[int, int]:
    alpha = secrets.randbelow(pp.N - 1)
    while alpha <= 2:
        alpha = secrets.randbelow(pp.N - 1)
    commitment = (pp.g * message)  +\
            (pp.h * alpha)
    return commitment, alpha

def pedersen_open(commitment: int, message: int, opening: int, pp: PedersenCommitmentPublicParams) -> bool:
    return commitment == \
            pp.g * message +\
            pp.h * opening