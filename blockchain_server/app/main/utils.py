from .. import db
from .models import Block, Transaction

def valid_chain(func=None):
    chain = db.session.query(Block).order_by(Block.index.asc()).all()
    idx = 1
    while idx < len(chain):
        nonce = chain[idx].nonce
        check_hash = chain[idx].__hash__(nonce)
        valid = check_hash == chain[idx].previous_hash
        if valid:
            idx += 1
        else:
            break
    
    response = {'valid': True, 'chain': chain}
    return response

        
def generate_genesis_block(address):
    if not db.session.query(Block).first():
        
        block = Block(
            index=0,
            miner=address
            )
        
        _hash, _nonce = Block._proof_of_work(block)
        
        block.previous_hash = _hash
        block.nonce = _nonce
        txs = Transaction.txs_to_block(block)
        block.transactions = txs
        
        db.session.add_all(txs)
        db.session.add(block)
        db.session.commit()
        
        print("genesis block created.")
        
        return block
    
    else:
        pass