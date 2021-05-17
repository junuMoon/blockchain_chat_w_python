import hashlib
import uuid
from datetime import datetime


class Blockchain(object):
    
    DIFFICULTY = 4
    FIRST_NONCE = 100
    
    
    def __init__(self):
        self.nodes = list()
        self.chain = list()
        self.current_transactions = list()
        
        self.root_node = self.new_node()
        _, nonce = self._proof_of_work(100)
        genesis_block = self.new_block(
            node_address=self.root_node.get('address')
        )

    def new_transaction(self, sender_address, recipient_address, amount, reward=False):
        
        transaction = {
            'timestamp': datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
            'sender_address': sender_address,
            'recipient_address': recipient_address,
            'amount': amount,
        }
        
        if reward == False:
            self.current_transactions.append(transaction)
        
        return transaction
    
    @staticmethod
    def _transaction_indexing(transactions):
        for i, transaction in enumerate(transactions):
            transaction.update({'index': i})
        
    def new_block(self, node_address):
        
        if len(self.chain) == 0:  # Genesis Block
            previous_hash, _nonce = self._proof_of_work(self.FIRST_NONCE)
        else:
            previous_hash, _nonce = self._proof_of_work(self.last_block)
            
        transactions = self.current_transactions
        reward_transaction = self.new_transaction(
            sender_address = "None",  # FIXME: none != null
            recipient_address = node_address,
            amount = 10, # FIXME: need int but get str from form data
            reward=True
        )
        transactions.insert(0, reward_transaction)
        self._transaction_indexing(transactions)
            
        block = {
            'index': len(self.chain),
            'timestamp': datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
            'miner': node_address,
            'previous_hash': previous_hash,
            'nonce': _nonce,
            'transactions': transactions
        }
        
        self.chain.append(block)
        self.current_transactions = list()
        
        return block
    
    def _valid_proof(self, block, nonce):
        _hash = hashlib.sha256(f"{block}{nonce}".encode()).hexdigest()
        return _hash, _hash[:self.DIFFICULTY] == "0" * self.DIFFICULTY

    def _proof_of_work(self, block):
        nonce = 0
        
        while True:
            _hash, _valid = self._valid_proof(block, nonce)
            if _valid == True:
                break
            else:
                nonce += 1
                
        return _hash, nonce
    
    
    def new_node(self, ip_address=None, address=None):
        if address == None:
            address = str(uuid.uuid4())
        node = {'ip_address': ip_address,
                'address': address}
        self.nodes.append(node)
        
        return node
    
    def valid_chain(self, chain):
        idx = 1
        while idx < len(chain):
            check_hash, _ = self._valid_proof(chain[idx-1], chain[idx].get('nonce'))
            print(f"check_hash: {check_hash}")
            print(f"target_hash: {chain[idx].get('previous_hash')}")
            if check_hash != chain[idx].get('previous_hash'):
                return False
            else:
                idx += 1
        return True
    
    @property
    def last_block(self):
        return self.chain[-1]

        
# blockchain = Blockchain()

