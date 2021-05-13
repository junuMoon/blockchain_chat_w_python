from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import hashlib

from flask import (Flask, request, redirect, render_template, url_for)

from urllib.parse import urlparse
from datetime import datetime
import json
import binascii



class Node:
    def __init__(self, address):
        self.address = address
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.public_key()
        

class Transaction:
    def __init__(self, sender, recipient_address, amount):
        self.index = 0
        self.time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        # self.previous_hash = blockchain.custom_hash(blockchain.current_transactions[-1])
        self.tx_detail = {
            'sender_address': binascii.hexlify(sender.public_key.export_key('OpenSSH')).decode(),
            'recipient_address': binascii.hexlify(recipient_address.export_key('OpenSSH')).decode(),
            'amount': amount
        }
        self.signature = self.sign_transaction(sender.private_key)
    
    def sign_transaction(self, sender_private_key):
        signer = pkcs1_15.new(sender_private_key)
        msg = json.dumps(self.tx_detail)
        h = SHA256.new(msg.encode())
        signature = signer.sign(h)
        
        return signature
        
        
class Block:
    INDEX = 0
    def __init__(self, previous_hash, transactions, nonce):
        self.index = self.INDEX
        self.previous_hash = previous_hash
        self.time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        self.transactions = transactions
        self.nonce = nonce


class Blockchain:
    
    DIFFICULTY = 4
    FIRST_NONCE = 100
    
    def __init__(self):
        self.nodes = set()
        self.MY_NODE = self.new_node(address="http://127.0.0.1:5000")
        
        self.chain = list()
        self.current_transactions = list()
        
        _, nonce = self._proof_of_work(self.FIRST_NONCE)
        genesis_block = Block(
            previous_hash= _,
            transactions=[Transaction(
                    self.MY_NODE,
                    self.MY_NODE.public_key,
                    10)],
            nonce=nonce
        )
        
        self.chain.append(genesis_block)
    
    def new_node(self, address):
        #TODO: get address
        parsed_url = urlparse(address)
        node = Node(parsed_url.netloc)
        self.nodes.add(node)
        
        return node
    
    def new_block(self):
        _hash, nonce = self._proof_of_work(self.last_block.__dict__)
        
        reward_transaction = Transaction(self.MY_NODE, self.MY_NODE.public_key, 10)
        self.current_transactions.insert(0, reward_transaction)
        
        for num, transaction in enumerate(self.current_transactions):
            transaction.index = num
        
        block = Block(
            previous_hash = _hash,
            transactions = self.current_transactions,
            nonce = nonce
        )
        self.chain.append(block)
        
        self.current_transactions = list()
        
        Block.INDEX += 1
        
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
    
    def verify_transaction(self, sender_public_key, tx):
        key = sender_public_key
        verifier = pkcs1_15.new(key)
        msg = json.dumps(tx.tx_detail)
        h = SHA256.new(msg.encode())
        verification = verifier.verify(h, tx.signature)
    
    def new_transaction(self, recipient_address, amount):
        tx = Transaction(
            self.MY_NODE,
            recipient_address,
            amount
        )
        
        try:
            self.verify_transaction(self.MY_NODE.public_key, tx)
            
            self.current_transactions.append(tx)
            
            return tx
        except:
            raise ValueError("Invalid Transaction")
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    @staticmethod
    def custom_hash(msg):
        msg = json.dumps(msg, sort_keys=True).encode()
        return hashlib.sha256(msg).hexdigest()
    


app = Flask(__name__)

blockchain = Blockchain()
kim = blockchain.new_node('http://127.0.0.1:5001')
blockchain.new_transaction(kim.public_key, 3)
blockchain.new_block()
blockchain.new_transaction(kim.public_key, 5)


@app.route('/', methods=['get'])
def index():
    transactions = list()
    
    for tx in blockchain.current_transactions:
        tx_json = json.dumps(tx.tx_detail)
        transactions.append(tx_json)
        
    blocks = [block.previous_hash for block in blockchain.chain]
        
    return render_template('index.html', blocks=blocks ,block_hash=None, transactions=transactions)


@app.route('/blocks/<string:block_hash>', methods=['get'])
def index_block(block_hash):
    
    blocks = [block.previous_hash for block in blockchain.chain]
    block = blockchain.chain[blocks.index(block_hash)]
    transactions = list()
    
    for tx in block.transactions:
        tx_json = json.dumps(tx.tx_detail)
        transactions.append(tx_json)

    return render_template('index.html', blocks=blocks, block_hash=block_hash, transactions=transactions)



@app.route('/blocks/mine/', methods=["GET"])
def mine():
    block_hash = blockchain.new_block().previous_hash
    message = "New block is created."
    
    return redirect(url_for('index_block', block_hash=block_hash, message=message))


@app.route('/transactions/new', methods=["GET", "POST"])
def submit_transaction():
    # "You can't unring the bell"
    if request.method == "GET":
        address = list()
        for node in blockchain.nodes:
            address.append(binascii.hexlify(node.public_key.export_key('OpenSSH')).decode())
        return render_template('transaction.html', address=address)
    
    elif request.method == "POST":
        recipient_address = request.form['recipient-address']
        recipient_address = RSA.import_key(binascii.unhexlify(recipient_address.encode()))
        amount = request.form['amount']
        
        blockchain.new_transaction(
            recipient_address=recipient_address,
            amount=amount)
        
        return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    



