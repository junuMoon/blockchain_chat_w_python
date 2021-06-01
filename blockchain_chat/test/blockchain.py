import hashlib
from datetime import datetime
from collections import OrderedDict

class HashedMessage(object):
    
    def __init__(self, username, data, previous_hash):
        self.timestamp = datetime.now().strftime('%Y-%m-%d')
        self.username = username
        self.data = data
        
        self.hash = self.custom_hash(previous_hash)
        
    def as_dict(self):
        d = OrderedDict(self.__dict__)
        return d

    def custom_hash(self, previous_hash):
        d = self.as_dict()
        d.update({'hash': previous_hash})
        
        msg = ''.join(list(d.values()))
        hash_id = hashlib.sha256(msg.encode()).hexdigest()
        return hash_id
    