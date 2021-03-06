import hashlib
from datetime import datetime
from functools import reduce

from sqlalchemy.orm import relationship

from .. import db


class Node(db.Model):
    __tablename__ = 'node'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String)
    address = db.Column(db.String(64))
    
    def __str__(self):
        return f"{self.ip_address} : {self.address}"
    
    def __repr__(self):
        return f"{self.ip_address} : {self.address}"
    
    
transaction_forwarding = db.Table(
    'transaction_forwarding',
    db.Column('tx_input', db.Integer, db.ForeignKey('transaction.hash')),
    db.Column('tx_output', db.Integer, db.ForeignKey('transaction.hash'))
)


class Transaction(db.Model):
    __tablename__ = 'transaction'
    REWARD = 10
    
    hash = db.Column(db.String(64), primary_key=True)
    added_to_block = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime)
    recipient = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    block_hash = db.Column(db.String(64), db.ForeignKey('block.previous_hash')) #TODO: ondelete
    block = db.relationship("Block", backref="transactions")
    
    tx_inputs = db.relationship(
        'Transaction',
        secondary=transaction_forwarding,
        primaryjoin=(transaction_forwarding.c.tx_input == hash),
        secondaryjoin=(transaction_forwarding.c.tx_output == hash),
        backref=db.backref('tx_outputs', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.timestamp=datetime.utcnow()
        self.hash = self.__hash__()
    
    def __str__(self):
        try:
            sender = self.tx_inputs.first().recipient
        except AttributeError:
            sender = None
        return f"{sender} -> {self.recipient} | {self.amount}"
    
    def __repr__(self):
        if self.block == None:
            return f"block[pending]: transaction <{self.hash[:10]}>"
        else:
            return f"block[{self.block.index}]: transaction <{self.hash[:10]}>"
        
    def to_dict(self):
        d = {
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        
        return dict(sorted(d.items()))
    
    def __hash__(self):
        d = self.to_dict()
        _hash = hashlib.sha256(str(d).encode()).hexdigest()
        
        return _hash
    
    @property
    def balance(self):
        balance = reduce(lambda x, y: x+y, [t.amount for t in self.tx_inputs.all()]) - self.amount
        assert balance >= 0
        return balance
    
    @staticmethod
    def _reward_transaction(block):
        tx = Transaction(
                recipient=block.miner,
                amount=Transaction.REWARD,
                )
        return tx
    
    @classmethod
    def txs_to_block(cls, block):
        txs = db.session.query(cls).filter(cls.added_to_block == False).order_by(cls.timestamp).all()
        txs.insert(0, cls._reward_transaction(block))
        
        for tx in txs:
            tx.added_to_block = True
            tx.block = block
            tx.block_hash = block.previous_hash
        
        return txs
        



class Block(db.Model):
    MINE_DIFFICULTY = 4
    FIRST_NONCE = 100
    __tablenames__ = 'block'
    
    previous_hash = db.Column(db.String(64), primary_key=True)
    timestamp = db.Column(db.DateTime)
    index = db.Column(db.Integer) #FIXME: unique constraint #FIXME: auto_increment
    miner = db.Column(db.String(100), nullable=False)
    nonce = db.Column(db.Integer)
    
    def __repr__(self):
        return f"block<{self.index}: {self.previous_hash[:10]}>"

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

    @staticmethod
    def _proof_of_work(block):
        nonce = 0
        
        while True:
            _hash = block.__hash__(nonce)
            if _hash[:Block.MINE_DIFFICULTY] == "0"*Block.MINE_DIFFICULTY:
                break
            else:
                nonce += 1
                
        return _hash, nonce

        
        
    #TODO: valid chain/block


    