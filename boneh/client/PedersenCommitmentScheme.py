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

pp = PedersenCommitmentPublicParams()
g_affine = pp.g.to_affine()
h_affine = pp.h.to_affine()
print(g_affine)
print(g_affine.x())
print(g_affine.y())
print(g_affine.curve())
p=115792089237316195423570985008687907853269984665640564039457584007908834671663
a=0
b=7
h=1
curve = ecdsa.ellipticcurve.CurveFp(p=p, a=a, b=b, h=h)
g_new = ecdsa.ellipticcurve.PointJacobi.from_affine(point=ecdsa.ellipticcurve.Point(curve, g_affine.x(), g_affine.y()))
h_new = ecdsa.ellipticcurve.PointJacobi.from_affine(point=ecdsa.ellipticcurve.Point(curve, h_affine.x(), h_affine.y()))

pp2 = PedersenCommitmentPublicParams()
pp2.g = g_new
pp2.h = h_new
commitment, opening = pedersen_commit(17, pp)
print(pedersen_open(commitment, 17, opening, pp2))

# g_new = ecdsa.ellipticcurve.PointJacobi.from_bytes(curve=ecdsa.SECP256k1, data=g_bytes)
# h_new = ecdsa.ellipticcurve.PointJacobi.from_bytes(pp.h.curve, h_bytes)
# print(pp.g == g_new)
# print(pp.h == h_new)