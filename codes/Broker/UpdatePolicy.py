from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from abenc_lwh import ABENCLWH
from charm.core.engine.util import objectToBytes,bytesToObject
import json
import hashlib
import yaml


class UpdatePolicy:
    def load_keys(self):
        with open('keys.yaml', 'r') as f:
            return yaml.safe_load(f)


    def update(self):
        with open("PolicyUpdateKey.yaml") as stream:
            try:
                uk_bytes = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        uk = bytesToObject(uk_bytes,PairingGroup('SS512'))
        # print(uk)
        I1 = uk['I1']
        I2 = uk['I2']
        I3 = uk['I3']
        type1_UK = list(uk['type1_UK'])
        type3_UK_1 = list(uk['type3_UK_1'])
        type3_UK_2 = list(uk['type3_UK_2'])
        type3_UK_3 = list(uk['type3_UK_3'])
        list_new = list(uk['new_shares_dict'])
        list_old = list(uk['old_shares_dict'])
        newPolicy = uk['policy']
        # print(type1_UK)

        with open("brokerCT.yaml") as stream:
            try:
                CT_bytes = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        CT = bytesToObject(CT_bytes,PairingGroup('SS512'))
        keys = self.load_keys()

        GPP = bytesToObject(keys['GPP'],PairingGroup('SS512'))
        authorities = bytesToObject(keys['authority'],PairingGroup('SS512'))
        # print(GPP)
        _, APK, authAttrs = authorities
        # keys = bytesToObject(keys_bytes,PairingGroup('SS512'))

    # update policy        
        for i, j in zip(I1, type1_UK):
            CT['C'][list_old[i[1]-1]] = CT['C'][list_old[i[1]-1]] * (GPP['g_a'] ** j) #update parameter 'C'

        for i, j1, j2, j3 in zip(I3, type3_UK_1, type3_UK_2, type3_UK_3):
            CT['C'][list_new[i[0]-1]] = j1
            CT['D'][list_new[i[0]-1]] = j2
            CT['DS'][list_new[i[0]-1]] = j3
        # print(CT)
        CT['policy'] = newPolicy
        # print(CT)

        new_CT = objectToBytes(CT, PairingGroup('SS512')).decode("utf-8")
        with open('brokerCT.yaml', 'w') as f:
            yaml.dump(new_CT, f)
        # with open("brokerCT.yaml") as stream:
        #     try:
        #         CT_bytes2 = yaml.safe_load(stream)
        #     except yaml.YAMLError as exc:
        #         print(exc)
        # CT2 = bytesToObject(CT_bytes2,PairingGroup('SS512'))
        # print(CT2)

if __name__ == '__main__':
    up = UpdatePolicy()
    up.update()