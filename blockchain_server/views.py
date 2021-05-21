from blockchain_server.utils import stringfy_block_hash
import sys
from collections import OrderedDict

import requests
from flask import Flask, jsonify, redirect, render_template, request, url_for, Blueprint

from blockchain_server.blockchain import Blockchain
from blockchain_server import db
from blockchain_server.models import Transaction, Block


# PORT = sys.argv[1]
PORT = 5000

blockchain = Blockchain()
blockchain.root_node['ip_address'] = '127.0.0.1:'+str(PORT)

bp = Blueprint('views', __name__)


@bp.route('/test/new_transaction')
def test_new_transaction():
    tx1 = Transaction(sender='Jong-min', recipient='you-kyoung', amount=1)
    tx2 = Transaction(sender='Jong-min', recipient='you-kyoung', amount=2)
    tx3 = Transaction(sender='Jong-min', recipient='you-kyoung', amount=3)
    
    
    db.session.add(tx1)
    db.session.add(tx2)
    db.session.add(tx3)
    db.session.commit()
    
    return tx1.__repr__()

@bp.route('/test/new_block')
def test_new_block():
    last_block = db.session.query(Block).order_by(Block.index.desc()).first()
    _hash, _nonce = last_block._proof_of_work()
    
    new_block = Block(previous_hash=_hash, miner='Junu', nonce=_nonce)
    
    txs = db.session.query(Transaction)\
        .filter(Transaction.added_to_block == False)\
            .order_by(Transaction.timestamp).all()
            
    transactions = list()
    for i, tx in enumerate(txs):
        tx.index = i
        tx.added_to_block = True
        tx.block = new_block
        tx.block_hash = new_block.previous_hash
        transactions.append(tx)
        db.session.add(tx)
        
    new_block.transactions = transactions
    new_block.index = last_block.index + 1
    db.session.add(new_block)
    db.session.commit()
    
    return new_block.to_dict()

@bp.route('/test/', methods=['GET'])
def test_index():
    transactions = db.session.query(Transaction).filter(Transaction.added_to_block == 0).all()
    blocks = [str(b).split("'")[1] for b in db.session.query(Block.previous_hash).all()]

    return render_template('index.html', blocks=blocks, transactions=transactions)
    

@bp.route('/', methods=['GET'])
def index():
    transactions = blockchain.current_transactions
    blocks = [block.get('previous_hash') for block in blockchain.chain]
    
    return render_template('index.html', blocks=blocks, transactions=transactions)


@bp.route('/test/blocks/<string:block_hash>', methods=['GET'])
def test_index_block(block_hash):
    blocks = [b.previous_hash for b in db.session.query(Block).order_by(Block.index).all()]
    b = db.session.query(Block).filter(Block.previous_hash == block_hash).first()
        
    transactions = [tx.to_dict() for tx in b.transactions]
    return render_template('index.html', blocks=blocks, block_hash=block_hash, transactions=transactions)


@bp.route('/blocks/<string:block_hash>', methods=['GET'])
def index_block(block_hash):
    blocks = [block.get('previous_hash') for block in blockchain.chain]

    for b in blockchain.chain:
        if b.get('previous_hash') == block_hash:
            block = b
            
    transactions = block['transactions']
    return render_template('index.html', blocks=blocks, block_hash=block_hash, transactions=transactions)


@bp.route('/test/blocks/mine/', methods=['GET'])
def test_mine():
    last_block = db.session.query(Block).order_by(Block.index.desc()).first()
    _hash, _nonce = last_block._proof_of_work()
    
    new_block = Block(previous_hash=_hash, miner='Junu', nonce=_nonce) #TODO: get miner from request
    print(new_block.previous_hash)
    txs = db.session.query(Transaction)\
        .filter(Transaction.added_to_block == False)\
            .order_by(Transaction.timestamp).all()
            
    transactions = list()
    for i, tx in enumerate(txs):
        tx.index = i
        tx.added_to_block = True
        tx.block = new_block
        tx.block_hash = new_block.previous_hash
        transactions.append(tx)
        db.session.add(tx)
        
    new_block.transactions = transactions
    new_block.index = last_block.index + 1
    db.session.add(new_block)
    db.session.commit()

    return redirect(url_for('views.test_index_block', block_hash=new_block.previous_hash))


@bp.route('/blocks/mine/', methods=['GET'])
def mine():
    block_hash = blockchain.new_block(blockchain.root_node['address']).get('previous_hash')
    message = 'New block is created.'
    
    return redirect(url_for('views.index_block', block_hash=block_hash))


@bp.route('/transactions/new', methods=['GET', 'POST'])
def submit_transaction():
    if request.method == 'GET':
        address = [node['address'] for node in blockchain.nodes]
        return render_template('new_transaction.html', address=address)
            
    if request.method == 'POST':
        # sender_address = request.form['sender-address']
        recipient_address = request.form['recipient-address']
        amount = int(request.form['amount'])
        
        blockchain.new_transaction(
            sender_address=blockchain.root_node['address'],
            recipient_address=recipient_address,
            amount = amount
        )
        
        return redirect(url_for('views.index'))
    
    
@bp.route('/nodes/register', methods=['POST'])
def register_node():
    new_node_ip = request.get_json().get('ip_address')
    
    if new_node_ip:
        try:
            requests.post(
                f"http://{new_node_ip}/nodes/accept/", 
                json={
                    'status': 1,
                    'ip_address': blockchain.root_node.get('ip_address'),
                    'address': blockchain.root_node.get('address'),
                    }
                )
        except:
            message = f"node's connection failed"

    return jsonify(new_node_ip), 201


@bp.route('/nodes/accept/', methods=['POST'])
def accept_node():
    
    try:
        values = request.get_json()
        address = values.get('address')
        ip_address = values.get('ip_address')
        print(ip_address, address)
        node = blockchain.new_node(ip_address, address)
        
        status = values.get('status')
        if status == 1:
            response = requests.post(f"http://{ip_address}/nodes/accept/",
                          json={
                                'status': 2,
                                'ip_address': blockchain.root_node.get('ip_address'),
                                'address': blockchain.root_node.get('address'),
            })
            print(response)
            
        message = f"New node [{node.get('address')}] has been added."
    except:
        message = f"node's connection failed"

    return jsonify(message)
    

@bp.route('/nodes/chain/', methods=['GET'])
def get_chain():
    if blockchain.valid_chain(blockchain.chain):
        return {'chain': blockchain.chain, 'code': 200}
    
    else:
        message = "no valid chain"
        return {'chain': [], 'message': message, 'code': 204}


@bp.route('/nodes/resolve', methods=['GET'])
def consensus():
    msg = f"Our chain is authoritative"
    
    for node in blockchain.nodes:

        ip_address = node.get('ip_address')
        new_chain = requests.get(f"http://{ip_address}/nodes/chain/").json().get('chain')
        
        if len(new_chain) > len(blockchain.chain):
            blockchain.replace_chain(new_chain)
        
            msg = f"Our chain was replaced with chain of {node}"

    return jsonify(msg), 201

