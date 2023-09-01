from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS

class ABENCLWH(DACMACS):
    def __init__(self, groupObj):
        self.util = SecretUtil(groupObj, verbose=False)  #Create Secret Sharing Scheme
        self.group = groupObj    #:Prime order group
    def setup(self):
        '''Global Setup (executed by CA)'''
        #:In global setup, a bilinear group G of prime order p is chosen
        #:The global public parameters, GP and p, and a generator g of G. A random oracle H maps global identities GID to elements of G
    
        #:group contains 
        #:the prime order p is contained somewhere within the group object
        g = self.group.random(G1)
        #: The oracle that maps global identities GID onto elements of G
        #:H = lambda str: g** group.hash(str)
        H = lambda x: self.group.hash(x, G1)
        a = self.group.random()
        g_a = g ** a
        GPP = {'g': g, 'g_a': g_a, 'H': H}
        GMK = {'a': a}
        
        return (GPP, GMK)

    # def registerUser(self, GPP):
    #     pass

    # def setupAuthority(self, GPP, authorityid, attributes, authorities):
    #     pass

    # def keygen(self, GPP, authority, attribute, userObj, USK = None):
    #     pass

    # def encrypt(self, GPP, policy_str, k, authority):
    #     pass

    # def generateTK(self, GPP, CT, UASK, g_u):
    #     pass

    # def decrypt(self, CT, TK, z):
    #     pass

    # def ukeygen(self, GPP, authority, attribute, userObj):
    #     pass

if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    dac = ABENCLWH(groupObj)