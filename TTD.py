import RSAGGen
# from sympy.ntheory.factor_ import totient
import hashlib
import random
from CCA_encryption import OneTimeKeyDeterministicAE

def pedersen_commit(RSAG, message):
    alpha = int(random.randint(1, RSAG.N - 1))
    commitment = (pow(RSAG.g, message, RSAG.N) * pow(RSAG.h, alpha, RSAG.N)) % RSAG.N
    return commitment, alpha

def pedersen_open(RSAG, commitment, message, opening):
    return commitment ==  (pow(RSAG.g, message, RSAG.N) * pow(RSAG.h, opening, RSAG.N)) % RSAG.N

def setup(lambda_, t):
    RSAG = RSAGGen.RSAG(lambda_, t)
    # euler's totient function - totient(N) = (q1-1)(q2-1) since we know that N = q1 * q2 where q1 and q2 are prime numbers
    z = pow(RSAG.h, pow(2, RSAG.t, (RSAG.q1 - 1) * (RSAG.q2 - 1)), RSAG.N)
    return RSAG, z

def TTD_commit(RSAG, message, z):
    commitment, opening = pedersen_commit(RSAG, message)
    alpha = random.randint(1, pow(2, RSAG.lambda_))
    H = pow(RSAG.h, alpha, RSAG.N)
    Z = pow(z, alpha, RSAG.N)
    enc_key = hashlib.sha256(str(Z).encode('utf-8')).hexdigest().encode('utf-8')
    ct = OneTimeKeyDeterministicAE.encrypt(enc_key, bytes(message), RSAG.t)
    return (commitment, )

# if __name__ == "__main__":
#     lambda_ = 256
#     RSAG, z = setup(lambda_, 3)
#     TTD_commit(RSAG, 12, z)