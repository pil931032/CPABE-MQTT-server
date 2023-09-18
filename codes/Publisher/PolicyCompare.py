from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
import yaml

class PolicyCompare:
    def __init__(self, groupObj):
        self.util = SecretUtil(groupObj, verbose=False)  #Create Secret Sharing Scheme
        self.group = groupObj    #:Prime order group

    def load_setting(self):
        with open('setting.yaml', 'r') as f:
            return yaml.safe_load(f)
        
    def compare(self): 
        setting = self.load_setting()
        old_policy_str = setting['Policy']
        new_policy_str = setting['NewPolicy']
        old_policy = self.util.createPolicy(old_policy_str)
        new_policy = self.util.createPolicy(new_policy_str)
        return(old_policy,new_policy)
    

if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    pc = PolicyCompare(groupObj)
    old,new=pc.compare()
    
    print(type(old))
    print(type(new))
