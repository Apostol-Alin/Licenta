import RSAGGen
import random
from PublicParameters import PublicParameters
from TC import TimedCommitment, TCOpening
import time

def pedersen_commit(message: int) -> tuple[int, int]:
    alpha = int(random.randint(1, PublicParameters.N - 1))
    commitment = (pow(PublicParameters.g, message, PublicParameters.N) * pow(PublicParameters.h, alpha, PublicParameters.N)) % PublicParameters.N
    return commitment, alpha

def pedersen_open(commitment: int, message: int, opening: int) -> bool:
    return commitment == (pow(PublicParameters.g, message, PublicParameters.N) * pow(PublicParameters.h, opening, PublicParameters.N)) % PublicParameters.N

def setup(lambda_, t):
    RSAG = RSAGGen.RSAG(lambda_, t)
    # euler's totient function - totient(N) = (q1-1)(q2-1) since we know that N = q1 * q2 where q1 and q2 are prime numbers
    z = pow(RSAG.h, pow(2, RSAG.t, (RSAG.q1 - 1) * (RSAG.q2 - 1)), RSAG.N)
    PublicParameters(lambda_, t, RSAG.h, RSAG.g, RSAG.N, z)

class TTDCommitment:
    def __init__(self, ped_commitment: int, timed_commitment_message: TimedCommitment, timed_commitment_ped_opening: TimedCommitment):
        self.ped_commitment = ped_commitment
        self.timed_commitment_message = timed_commitment_message
        self.timed_commitment_ped_opening = timed_commitment_ped_opening

class TTDOpening:
    def __init__(self, tc_opening_message: TCOpening, tc_opening_ped_opening: TCOpening):
        self.tc_opening_message = tc_opening_message
        self.tc_opening_ped_opening = tc_opening_ped_opening

def TTD_commit(message: int) -> tuple[TTDCommitment, TTDOpening, int]:
    ped_commitment, ped_opening = pedersen_commit(message)
    # need to time commit the pair (message, ped_opening)

    # Problem right now is that we need to time commit them independently
    # Ideally, we want to commit the pair as a whole
    # Then from the decrypted value of the timed commit parse: (message, ped_opening) <- dec_tc_value
    ped_opening_bytes = ped_opening.to_bytes((ped_opening.bit_length() + 7) // 8, byteorder='big')
    messsage_bytes = message.to_bytes((message.bit_length() + 7) // 8, byteorder='big')
    tc_message, tc_opening_message = TimedCommitment.commit(messsage_bytes)
    tc_ped_opening, tc_opening_ped_opening = TimedCommitment.commit(ped_opening_bytes)

    # return all the commitments made and the openings of the timed commitments and the pedersen commitment opening for the commiter
    return TTDCommitment(ped_commitment, tc_message, tc_ped_opening), TTDOpening(tc_opening_message, tc_opening_ped_opening), ped_opening

def TTD_verify_opening(message: bytes, ped_opening: bytes, ttd_com: TTDCommitment, ttd_open: TTDOpening) -> bool:
    if TimedCommitment.verify_opening(message, ttd_com.timed_commitment_message, ttd_open.tc_opening_message) and \
       TimedCommitment.verify_opening(ped_opening, ttd_com.timed_commitment_ped_opening, ttd_open.tc_opening_ped_opening):
        message_value = int.from_bytes(message, byteorder='big')
        ped_opening_value = int.from_bytes(ped_opening, byteorder='big')
        if pedersen_open(ttd_com.ped_commitment, message_value, ped_opening_value):
            return True
        return False
    else:
        return False

if __name__ == "__main__":
    lambda_ = 256
    t = pow(2, 23)
    message = 1999
    setup(lambda_, t)

    com, open, ped_opening = TTD_commit(message)
    message_bytes = message.to_bytes((message.bit_length() + 7) // 8, byteorder='big')
    ped_opening_bytes = ped_opening.to_bytes((ped_opening.bit_length() + 7) // 8, byteorder='big')
    print(TTD_verify_opening(message_bytes, ped_opening_bytes, com, open))

    start_force = time.time()
    print("Started force opening for the message...")
    force_message, force_opening_message = TimedCommitment.force_open(com.timed_commitment_message)
    print(f"Force opening time duration: {time.time() - start_force} seconds")

    start_force = time.time()
    print("Started force opening for the pedersen opening...")
    force_ped_comm, force_opening_ped_opening = TimedCommitment.force_open(com.timed_commitment_ped_opening)
    print(f"Force opening time duration: {time.time() - start_force} seconds")

    force_ttd_open = TTDOpening(force_opening_message, force_opening_ped_opening)
    print(TTD_verify_opening(force_message, force_ped_comm, com, force_ttd_open))
