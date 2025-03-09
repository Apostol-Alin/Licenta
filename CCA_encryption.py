import hashlib
import struct

class OneTimeKeyDeterministicAE:
    @staticmethod
    def encrypt(key: bytes, pt: bytes, ad: bytes) -> bytes:
        assert len(key) == 32
        enc_key = key[:16]
        mac_key = key[16:]

        ct = OneTimeKeyDeterministicAE.one_time_pad(enc_key, pt)
        mac = hashlib.sha256(mac_key + ct + ad).digest()
        return ct + mac  # Append MAC to ciphertext

    @staticmethod
    def decrypt(key: bytes, ct_mac: bytes, ad: bytes) -> bytes:
        assert len(key) == 32
        enc_key = key[:16]
        mac_key = key[16:]

        ct, received_mac = ct_mac[:-32], ct_mac[-32:]  # Separate ciphertext and MAC
        computed_mac = hashlib.sha256(mac_key + ct + ad).digest()

        if received_mac == computed_mac:
            return OneTimeKeyDeterministicAE.one_time_pad(enc_key, ct)
        else:
            raise ValueError("Decryption failed: MAC verification failed")

    @staticmethod
    def one_time_pad(key: bytes, data: bytes) -> bytes:
        block_size = 32
        num_blocks = (len(data) + block_size - 1) // block_size  # Round up

        pad = b"".join(
            hashlib.sha256(key + struct.pack("B", i)).digest()
            for i in range(num_blocks)
        )[:len(data)]

        return bytes(d ^ p for d, p in zip(data, pad))  # XOR with keystream
