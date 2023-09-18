from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS

class ABENCLWH(DACMACS):
    def __init__(self):
        pass

    def setup(self):
        pass

    def registerUser(self, GPP):
        pass

    def setupAuthority(self, GPP, authorityid, attributes, authorities):
        pass

    def keygen(self, GPP, authority, attribute, userObj, USK = None):
        pass

    def encrypt(self, GPP, policy_str, k, authority):
        pass

    def generateTK(self, GPP, CT, UASK, g_u):
        pass

    def decrypt(self, CT, TK, z):
        pass

    def ukeygen(self, GPP, authority, attribute, userObj):
        pass