from ast import dump
import hashlib, random, string

def dumb_hash(message):
    """
    Args:
        message (str): a string of arbitrary length

    Returns:
        hash: a fixed-length string of 64 hexadecimal characters.
    """
    return hashlib.sha256(message.encode()).hexdigest()

def mine(message, difficulty=1):
    """
    Given an input string, will return a nonce such that
    hash(string + nonce) starts with `difficulty` ones
    
    Returns: (nonce, niters)
        nonce: The found nonce
        niters: The number of iterations required to find the nonce
    """
    assert difficulty >= 1
    i = 0
    prefix = '1' * difficulty
    while True:
        nonce = str(i)
        digest = dumb_hash(message + nonce)
        if digest.startswith(prefix):
            return nonce
        i += 1
        
def random_string(length=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii


class Wallet:
    """A wallet is a private/public key pair"""
    def __init__(self):
        random_gen = Crypto.Random.new().read
        self._private_key = RSA.generate(1024, random_gen)
        self._public_key = self._private_key.public_key()
        self._signer = PKCS1_v1_5.new(self._private_key)
        
    @property
    def address(self):
        """We take a shortcut and say address is public key"""
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode()
    
    def sign(self, message):
        """Sign a message with this wallet"""
        h = SHA.new(message.encode())
        return binascii.hexlify(self._signer.sign(h)).decode()
    
def verify_signature(wallet_address, message, signature):
    """
    Check that the provided 'signature' corresponds to 'message'
    signed by the wallet at 'wallet_address'
    """
    pubkey = RSA.importKey(binascii.unhexlify(wallet_address))
    verifier = PKCS1_v1_5.new(pubkey)
    h = SHA.new(message.encode())
    return verifier.verify(h, binascii.unhexlify(signature))
    

class TransactionInput(object):
    """An input for a transaction. This points to an output of last transaction"""
    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index
        assert 0 <= self.output_index < len(transaction.outputs)
        
    def to_dict(self):
        d = {
            'transaction': self.transaction.hash(),
            'output_index': self.output_index
        }
        return d
    

class TransactionOutput(object):
    """An output for a transaction. This specifies an amount and a recipient(wallet)"""
    def __init__(self, recipient_address, amount):
        self.recipient = recipient_address
        self.amount = amount
        
    def to_dict(self):
        d = {
            'recipient_address': self.recipient,
            'amount': self.amount
        }
        return d

def compute_fee(inputs, outputs):
    total_in = sum(i.transaction.outputs[i.output_index].amount for i in inputs)
    total_out = sum(o.amount for o in outputs)
    assert total_out < total_in, f"Invalid transaction with out({total_out} > in in({total_in})"
    return total_in - total_out


import json


class Transaction(object):
    def __init__(self, wallet, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.fee = compute_fee(inputs, outputs)
        self.signature = wallet.sign(json.dumps(self.to_dict(include_signature=False)))
        
    def to_dict(self, include_signature=True):
        d = {
            "inputs": list(map(TransactionInput.to_dict, self.inputs)),
            "outputs": list(map(TransactionOutput.to_dict, self.outputs)),
            "fee": self.fee
        }
        if include_signature:
            d["signature"] = self.signature
        return d
    
    def hash(self):
        return dumb_hash(json.dumps(self.to_dict()))
    

class GenesisTransaction(Transaction):
    """
    This is the fisrt transaction which is a special transaction
    with no input and 25 bitcoins output
    """
    def __init__(self, recipient_address, amount=25):
        self.inputs = []
        self.outputs = [
            TransactionOutput(recipient_address, amount)
        ]
        self.fee = 0
        self.signature = 'genesis'
        
    def to_dict(self, include_signature=False):
        assert not include_signature, "Cannot include signature of genesis transaction"
        return super().to_dict(include_signature=False)
    
alice = Wallet()
bob = Wallet()

import numpy as np

t1 = GenesisTransaction(alice.address)
t2 = Transaction(
    alice,
    [TransactionInput(t1, 0)],
    [TransactionOutput(bob.address, 2.0), TransactionOutput(alice.address, 22.0)]
)
assert np.abs(t2.fee - 1.0) < 1e-5
