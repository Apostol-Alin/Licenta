import RSAGGen
# from sympy.ntheory.factor_ import totient
import hashlib
import random
from CCA_encryption import OneTimeKeyDeterministicAE
import PublicParameters
import TC

def pedersen_commit(message: int) -> tuple[int, int]:
    alpha = int(random.randint(1, PublicParameters.N - 1))
    commitment = (pow(PublicParameters.g, message, PublicParameters.N) * pow(PublicParameters.h, alpha, PublicParameters.N)) % PublicParameters.N
    return commitment, alpha

def pedersen_open(commitment: int, message: int, opening: int) -> bool:
    return commitment ==  (pow(PublicParameters.g, message, PublicParameters.N) * pow(PublicParameters.h, opening, PublicParameters.N)) % PublicParameters.N

def setup(lambda_, t):
    RSAG = RSAGGen.RSAG(lambda_, t)
    # euler's totient function - totient(N) = (q1-1)(q2-1) since we know that N = q1 * q2 where q1 and q2 are prime numbers
    z = pow(RSAG.h, pow(2, RSAG.t, (RSAG.q1 - 1) * (RSAG.q2 - 1)), RSAG.N)
    PublicParameters.PublicParameters(lambda_, t, RSAG.h, RSAG.g, RSAG.N, RSAG.z)
    return RSAG, z

def TTD_commit(message: int):
    ped_commitment, ped_opening = pedersen_commit(message)
    # need to time commit the pair (message, ped_opening)
    # both are int -> represent them as hexadecimal values
    # append them togheter in a string
    # bytes(result)
    # time commit the bytes

    hex_message = str(hex(message))
    hex_ped_opening = str(hex(ped_opening))
    val = f"0x{hex_message[2:]}{hex_ped_opening[2:]}"
    val = bytes(val.encode('utf-8'))

    tc, tc_opening = TC.TimedCommitment.commit(val)

    return (ped_commitment, ped_opening), (tc, tc_opening)

def TTD_verify_opening(message: bytes, tc: TC.TimedCommitment, opening: TC.TCOpening):
    valid_tc = TC.TimedCommitment.verify_opening(message, )

if __name__ == "__main__":
    a = 23123
    b = 90323    
    a = hex(a)
    b = hex(b)
    str_a = str(a)[2:]
    str_b = str(b)[2:]
    print(str_a)
    print(str_b)
    comb = f"0x{str_a}{str_b}"
    print(bytes(comb.encode('utf-8')))
    bytes_comb = bytes(comb.encode('utf-8'))
    back_to_string = bytes_comb.decode()[2:]
    print(back_to_string)
    back_to_a = back_to_string[:len(str_a)]
    back_to_b = back_to_string[len(str_a):len(str_a) + len(str_b)]
    print(back_to_a)
    print(back_to_b)
    print(int(back_to_a, 16))
    print(int(back_to_b, 16))


    