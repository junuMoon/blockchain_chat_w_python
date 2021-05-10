import hashlib
import json
from Crypto.PublicKey import RSA

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
    FIRST_NONCE = 100
    
    def __init__(self):
        self.nodes = list()
        self.chain = list()
        self.current_transactions = list()
        
        _, nonce = self._proof_of_work(self.FIRST_NONCE)
        genesis_block = Block(
            previous_hash= '',
            transactions=list(),
            nonce=nonce
        )
        
        self.chain.append(genesis_block)
        
    def new_block(self):
        _hash, nonce = self._proof_of_work(self.last_block.__dict__)
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
        
    def _proof_of_work(self, block):
        nonce = 0
        
        while True:
            _hash = hashlib.sha256(f"{block}{nonce}".encode()).hexdigest()
            if _hash[:self.DIFFICULTY] == "0"*self.DIFFICULTY:
                break
            else:
                nonce += 1
        return _hash, nonce
                
    def new_transactions(self, sender_address, recipient_address, amount):
        tx = Transaction(
            sender = sender_address,
            recipient_address = recipient_address,
            amount = amount
        )
        Transaction.INDEX += 1
        self.current_transactions.append(tx)
        return tx
        
        
    def new_node(self, nickname):
        nickname = nickname
        private_key = RSA.generate(2048)
        public_key = private_key.public_key()
        node = {
            'name': nickname,
            'private_key': private_key,
            'public_key': public_key
        }
        self.nodes.append(node)

    @staticmethod
    def custom_hash(msg):
        msg = json.dumps(msg)
        return hashlib.sha256(msg.encode()).hexdigest()
    
    @property
    def last_block(self):
        return self.chain[-1]
    

blockchain = Blockchain()
blockchain.new_block()