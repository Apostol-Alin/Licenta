class PublicParameters:
    def __init__(self, lambda_: int, t: int, h: int, g: int, N: int, z: int):
        PublicParameters.lambda_ = lambda_ # security parameter
        PublicParameters.t = t # time parameter
        PublicParameters.h = h # RSAG generator h
        PublicParameters.g = g # RSAG generator g
        PublicParameters.N = N # order of RSAG
        PublicParameters.z = z