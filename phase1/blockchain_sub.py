import hashlib
import json


class Transaction:
    INDEX = 0
    
    def __init__(self, sender, recipient_address, amount):
        self.index = self.INDEX
        self.previous_hash = ''
        self.timestamp = '2020-04-10'
        self.sender = sender
        self.recipient_address = recipient_address
        self.amount = amount

class Block:
    INDEX = 0
    
    def __init__(self, previous_hash, transactions, nonce):
        self.index = self.INDEX
        self.previous_hash = previous_hash
        self.timestamp = '2020-04-10'
        self.transactions = transactions
        self.nonce = nonce
        

class Blockchain:
    
    DIFFICULTY = 4
    
    def __init__(self):
        self.nodes = set()
        self.chain = list()
        self.current_transactions = list()
        
        _hash, nonce = self.proof_of_work(100)
        genesis_block = Block(
            previous_hash= _hash,
            transactions=list(),
            nonce=nonce
        )
        
        self.chain.append(genesis_block)
        
    def new_block(self):
        _hash, nonce = self.proof_of_work(self.last_block.__dict__)
        block = Block(
            previous_hash = _hash,
            transactions = self.current_transactions,
            nonce = nonce
        )
        self.chain.append(block)
        self.current_transactions = list()
        Block.INDEX += 1
        Transaction.INDEX = 0
        
        return block
        
    def proof_of_work(self, msg):
        nonce = 0
        
        while True:
            _hash = hashlib.sha256(f"{msg}{nonce}".encode()).hexdigest()
            if _hash[:self.DIFFICULTY] == "0"*self.DIFFICULTY:
                return _hash, nonce
                break
            else:
                nonce += 1
                
    def new_transactions(self):
        tx = Transaction(
            sender = input(),
            recipient_address = input(),
            amount = input()
        )
        Transaction.INDEX += 1

    @staticmethod
    def custom_hash(msg):
        msg = json.dumps(msg)
        return hashlib.sha256(msg.encode()).hexdigest()
    
    @property
    def last_block(self):
        return self.chain[-1]
    
blockchain = Blockchain()
blockchain.new_block()