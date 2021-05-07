from collections import OrderedDict
from phase1.blockchain import verify_signature

class Transaction:
    def __init__(self, sender_address, send_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.send_private_key = send_private_key
        self.recipient_address =  recipient_address
        self.value = value
        
    def __getter__(self, attr):
        return self.data[attr]
    
    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value})
        
    def sign_transaction(self):
        return verify_signature(self.sender_address, self, self.sender_address)
        
        
    
    
class GenesisTransaction(Transaction):
    def __init__(self):
        pass