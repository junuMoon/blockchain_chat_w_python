from sqlalchemy.orm import backref, relationship
from blockchain_server import db
from datetime import datetime
import hashlib


class Transaction(db.Model):
    __tablename__ = 'transaction'
    
    hash = db.Column(db.String(64), primary_key=True)
    index = db.Column(db.String)
    added_to_block = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime)
    sender = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    block_hash = db.Column(db.String(64), db.ForeignKey('block.previous_hash')) #TODO: ondelete
    block = db.relationship("Block", backref="transactions")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.timestamp=datetime.utcnow()
        self.hash = self.__hash__()
    
    def __str__(self):
        return f"{self.sender} transferred {self.amount} to {self.recipient}"
    
    def __repr__(self):
        if self.block == None:
            return f"block[pending]: transaction <{self.hash}"
        else:
            return f"block[{self.block.index}]: transaction {self.index} - [{self.hash}]"
        
    def to_dict(self):
        d = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        
        return dict(sorted(d.items()))
    
    def __hash__(self):
        d = self.to_dict()
        _hash = hashlib.sha256(str(d).encode()).hexdigest()
        
        return _hash
    
    #TODO: reward transaction
    

MINE_DIFFICULTY = 4

class Block(db.Model):
    __tablenames__ = 'block'
    
    previous_hash = db.Column(db.String(64), primary_key=True)
    timestamp = db.Column(db.DateTime)
    index = db.Column(db.Integer) #FIXME: unique constraint #FIXME: auto_increment
    miner = db.Column(db.String(100), nullable=False)
    nonce = db.Column(db.Integer)
    
    def __repr__(self):
        return f"block<{self.index}: {self.previous_hash}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.timestamp=datetime.utcnow()
    
    def to_dict(self):
        d = {
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp, #TODO: strptime
            'miner': self.miner,
            'nonce': self.nonce,
            'transactions': [tx.to_dict() for tx in self.transactions]
        }

        return dict(sorted(d.items()))
    
    def __hash__(self, nonce=None):
        if not nonce:
            nonce = ''
        d = self.to_dict()
        _hash = hashlib.sha256(f"{d}{nonce}".encode()).hexdigest()
        
        return _hash

    def _proof_of_work(self):
        nonce = 0
        
        while True:
            _hash = self.__hash__(nonce)
            if _hash[:MINE_DIFFICULTY] == "0"*MINE_DIFFICULTY:
                break
            else:
                nonce += 1
                
        return _hash, nonce

    #TODO: genesis block
    #TODO: valid chain/block


    