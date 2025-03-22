from __future__ import annotations
import hashlib
import random
from CCA_encryption import OneTimeKeyDeterministicAE
from PublicParameters import PublicParameters
import time

class TCOpening:
    def __init__(self, opening_value, mode):
        self.opening_value = opening_value # either alpha or Z based on opening mode (alpha for COMMITER and Z for FORCE)
        self.mode = mode # mode is either "COMMITER" or "FORCE"

class TimedCommitment:
    def __init__(self, ct: bytes, H: int):
        self.ct = ct
        self.H = H

    @staticmethod
    def commit(message: bytes) -> tuple[TimedCommitment, TCOpening]:
        alpha = random.randint(1, pow(2, PublicParameters.lambda_))
        H = pow(PublicParameters.h, alpha, PublicParameters.N)
        Z = pow(PublicParameters.z, alpha, PublicParameters.N)
        enc_key = hashlib.sha256(str(Z).encode('utf-8')).digest()
        t = PublicParameters.t
        t = t.to_bytes((t.bit_length() + 7) // 8 or 1)
        ct = OneTimeKeyDeterministicAE.encrypt(enc_key, message, t)
        # Use the time parameter as additional data
        return TimedCommitment(ct, H), TCOpening(alpha, "COMMITER")

    @staticmethod
    def force_open(tc: TimedCommitment) -> tuple[bytes, TCOpening]:
        Z = pow(tc.H, pow(2, PublicParameters.t), PublicParameters.N)
        # TODO: add proof of exponentation
        enc_key = hashlib.sha256(str(Z).encode('utf-8')).digest()
        t = PublicParameters.t
        t = t.to_bytes((t.bit_length() + 7) // 8 or 1)
        message = OneTimeKeyDeterministicAE.decrypt(enc_key, tc.ct, t)
        return message, TCOpening(Z, "FORCE")
    @staticmethod
    def verify_opening(message: bytes, tc: TimedCommitment, opening: TCOpening):
        if opening.mode == 'FORCE':
            Z = opening.opening_value
            enc_key = hashlib.sha256(str(Z).encode('utf-8')).digest() # use the same hash function to obtain encryption key
            t = PublicParameters.t
            t = t.to_bytes((t.bit_length() + 7) // 8 or 1)
            pt = OneTimeKeyDeterministicAE.decrypt(enc_key, tc.ct, t)
            # TODO: add proof of exponentiation verification
            if str(pt).encode('utf-8') != str(message).encode('utf-8'):
                return False
            return True
        elif opening.mode == 'COMMITER':
            alpha = opening.opening_value # here we receive as opening value the random value used to compute Z
            Z = pow(PublicParameters.z, alpha, PublicParameters.N) # we calculate Z based on received alpha
            enc_key = hashlib.sha256(str(Z).encode('utf-8')).digest() # use the same hash function to obtain encryption key
            t = PublicParameters.t
            t = t.to_bytes((t.bit_length() + 7) // 8 or 1)
            pt = OneTimeKeyDeterministicAE.decrypt(enc_key, tc.ct, t)
            if pow(PublicParameters.h, alpha, PublicParameters.N) != tc.H:
                # check that the obtained alpha is the one commited in H from the timed commitment
                return False
            if str(pt).encode('utf-8') != str(message).encode('utf-8'):
                return False
            return True
        else:
            raise ValueError(f"Expected opening.mode either FORCE or COMMITER, but found {opening.mode}")

if __name__ == "__main__":
    print("Hi")
    # lambda_ = 256
    # t = pow(2, 25)
    # RSAG, z = TTD.setup(lambda_, t)
    # PublicParameters(lambda_, t, RSAG.h, RSAG.g, RSAG.N, z)
    # message = bytes("Hello, Alin!".encode('utf-8'))
    # commitment, opening = TimedCommitment.commit(message)
    # print(TimedCommitment.verify_opening(message, commitment, opening))

    # alpha = opening.opening_value
    # H = pow(RSAG.h, alpha, RSAG.N)
    # Z_CALC = pow(H, pow(2, PublicParameters.t), PublicParameters.N)

    # print(Z)
    # print(Z_CALC)

    # print(commitment.ct)
    # enc_key = hashlib.sha256(str(Z).encode('utf-8')).digest()
    # t = PublicParameters.t
    # t = t.to_bytes((t.bit_length() + 7) // 8 or 1)
    # pt = OneTimeKeyDeterministicAE.decrypt(enc_key, commitment.ct, t)
    # print(pt)
    # start_force = time.time()
    # print("Started force opening...")
    # forced_message, forced_opening = TimedCommitment.force_open(commitment)
    # print(f"Force opening time duration: {time.time() - start_force} seconds")
    # print(TimedCommitment.verify_opening(forced_message, commitment, forced_opening))
    # print(str(forced_message))
    # print(pow(PublicParameters.z, opening.opening_value, PublicParameters.N))
    # print(forced_opening.opening_value)
    # print(opening.opening_value == forced_opening.opening_value)