from hashlib import sha256
import json
import time

class Transaction:
    def __init__(self, sender, recipient):
        self.sender
        self.recipient
        self.timestamp = time.timestamp()


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = set()
        self.previous_hash = previous_hash
        self.nonce = nonce
        
    def hash(self):
        pass
    
    def submit_transaction(self):
        pass
    
    
class Blockchain:
    def __init__(self):
        self.chain = list()
        self.nodes = set()
        
    def new_block(self):
        block = Block()
        
    def _get_all_nodes(self):
        pass
        
        