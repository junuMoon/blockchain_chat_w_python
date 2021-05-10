import hashlib
import binascii
import json
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA

class Node:
    INDEX = 0
    
    def __init__(self, nickname):
        self.index = self.INDEX
        self.nickname = nickname
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.public_key()
        
class Transaction:
    INDEX = 0
    
    def __init__(self, sender_address, recipient_address, amount):
        self.index = self.INDEX
        self.previous_hash = ''
        self.timestamp = '2020-04-10'
        self.sender = sender_address
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
                
    def new_transactions(self, sender, recipient_address, amount):
        
        signature = sender.public_key
        
        tx = Transaction(
            sender = sender.public_key,
            recipient_address = recipient.public_key,
            amount = amount
        )
        Transaction.INDEX += 1
        self.current_transactions.append(tx)
        return tx
        
# 1. sender는 이전 tx를 recipient address를 넣고 asymmetric encryption로 잠군다. -> enc_msg
# 2. sender priv key를 넣고 enc_msg에 digital signature를 남긴다.
# 3. recipient는 sender의 public key를 넣고 digital signature가 진본임을 확인한다.
# 4. recipient는 priv key로 tx을 푼다
    def new_node(self, nickname):
        nickname = nickname
        node = Node(nickname)
        Node.INDEX += 1
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