from ipaddress import ip_address
from flask import jsonify, redirect, render_template, request, url_for, session, current_app

import requests

from sqlalchemy.sql.expression import func

from .. import db
from .models import Block, Transaction, Node
from . import main


@main.before_app_first_request
def generate_genesis_block():
    if not db.session.query(Block).first():
        
        block = Block(
            index=0,
            miner="Satoshi Nakamoto"
            )
        
        _hash, _nonce = Block._proof_of_work(block)
        
        block.previous_hash = _hash
        block.nonce = _nonce
        txs = Transaction.txs_to_block(block)
        block.transactions = txs
        
        db.session.add_all(txs)
        db.session.add(block)
        db.session.commit()
    

@main.route('/', methods=['GET'])
def index():
    transactions = db.session.query(Transaction).filter(Transaction.added_to_block == 0).all()
    blocks = [str(b).split("'")[1] for b in db.session.query(Block.previous_hash).all()]
    print(CONNECT_NODES)

    #TODO: valid chain
    return render_template('index.html', blocks=blocks, transactions=transactions, nodes=CONNECT_NODES)


@main.route('/blocks/<string:block_hash>', methods=['GET'])
def index_block(block_hash):
    blocks = [b.previous_hash for b in db.session.query(Block).order_by(Block.index.desc()).all()]
    b = db.session.query(Block).filter(Block.previous_hash == block_hash).first()
        
    #TODO: valid chain
    transactions = [tx.to_dict() for tx in b.transactions]
    return render_template('index.html', blocks=blocks, block_hash=block_hash, transactions=transactions)


@main.route('/blocks/mine/', methods=['GET'])
def mine():
    last_block = db.session.query(Block).order_by(Block.index.desc()).first()
    _hash, _nonce = Block._proof_of_work(last_block)
    
    new_block = Block(previous_hash=_hash,
                      miner=session['node-address'],
                      nonce=_nonce)
    
    txs = Transaction.txs_to_block(new_block)
        
    new_block.transactions = txs
    new_block.index = last_block.index + 1
    # print(new_block.__dict__)
    db.session.add_all(txs)
    db.session.add(new_block)
    db.session.commit()
    
#     message = 'New block is created.'

    return redirect(url_for('.index_block', block_hash=new_block.previous_hash))


@main.route('/transactions/new', methods=['GET', 'POST'])
def submit_transaction():
    if request.method == 'GET':
        address_list = [node.address for node in db.session.query(Node).all()]
        return render_template('new_transaction.html', data=address_list)
    
    elif request.method == 'POST':
        sender_address = request.form['sender-address']
        recipient_address = request.form['recipient-address']
        amount = int(request.form['amount'])
        
        new_tx = Transaction(sender=sender_address,
                             recipient=recipient_address,
                             amount=amount)
        
        db.session.add(new_tx)
        db.session.commit()
        
        return redirect(url_for('.index'))
    

CONNECT_NODES_NUM = 5
CONNECT_NODES = list()
CONNECT_NODES_SEAT = CONNECT_NODES_NUM - len(CONNECT_NODES)


@main.before_app_request
def node_session():
    node = db.session.query(Node).filter(Node.ip_address=='127.0.0.1:'+current_app.config['PORT']).first()
    if node:
        session['node-ip-address'] = node.ip_address
        session['node-address'] = node.address

@main.route('/nodes/register', methods=['GET', 'POST'])
def node_register():
    if request.method == 'GET':
        if session['node-ip-address']:
            return render_template('index.html')
        
        else:
            return render_template('nodes_register.html')
        
    
    elif request.method == 'POST':
        node = db.session.query(Node).filter(Node.ip_address=='127.0.0.1'+current_app.config['PORT']).first()
        address = request.form['address']
        node = Node(ip_address='127.0.0.1:'+current_app.config['PORT'], address=address)
        db.session.add(node)
        db.session.commit()
            
        session['node-ip-address'] = node.ip_address
        session['node-address'] = node.address

        return redirect(url_for('.index'))
    

@main.route('/nodes/connect/', methods=['GET', 'POST'])
def connect_nodes():
    
    if request.method == 'GET':
        
        nodes = db.session.query(Node).filter(Node.ip_address!=session['node-ip-address']).order_by(func.random()).limit(CONNECT_NODES_SEAT).all()
        
        for node in nodes:
            try:
                #TODO: asynchronous connection
                requests.post(f"http://{node.ip_address}/nodes/accept/",
                            json={
                                'ip_address': session['node-ip-address'],
                                'address': session['node-address']
                            })
            except Exception as e:
                message = f"Connection to {node.ip_address} has failed"
                print(e, message)
        
        return redirect(url_for('.index'))
                
    elif request.method == 'POST':
        
        if request.get_json().get('status') == 0:
            message = ''
            
        elif request.get_json().get('status') == 1:
            try:
                values = request.get_json()
                print(values)
                
                new_node_ip_address = values.get('ip_address')
                new_node = db.sessions.query(Node).filter(Node.ip_address==new_node_ip_address).first()
                CONNECT_NODES.append(new_node)
            except:
                print("wrong")
        return message


@main.route('/nodes/accept/', methods=['POST'])
def accept_node():
    try:
        values = request.get_json()
        print(values)
        
        new_node_address = values.get('address')
        new_node_ip_address = values.get('ip_address')
        
        if not CONNECT_NODES_SEAT:
            print('5')
            response = requests.post(f"http://{new_node_ip_address}/nodes/connect/",
                                json={
                                    'status': 0,
                                    'ip_address': session['node-ip-address'],
                                    'address': session['node-address'],
                                    'message': "{session['node-ip-address']} has no seat for connection"
                                })
            return response

        else:

            new_node = db.session.query(Node).filter(Node.ip_address==new_node_ip_address).first()
            if not new_node:
                new_node = Node(ip_address=new_node_ip_address,
                            address=new_node_address)
                db.session.add(new_node)
                db.session.commit()
            
            print('new_node2', new_node)

            CONNECT_NODES.append(new_node)
            
            if not values.get('status'):
                response = requests.post(f"http://{new_node_ip_address}/nodes/accept/",
                                        json = {
                    'status': 1,
                    'ip_address': session['node-ip-address'],
                    'address': session['node-address'],
                    'message': "Connections between {session['node-ip-address']} - {new_node_ip_address} has been established."
                })

            return 200
    
    except Exception as e:
        print(e)
        return f"Error occurred: {e}"


def tear_down():
    for node in CONNECT_NODES:
        response = requests.post(f"http://{node.ip_address}/nodes/connect/",
                json={
                    'status': 2,
                    'ip_address': session['node-ip-address'],
                    'address': session['node-address'],
                    'message': "{session['node-ip-address']} has left the server."
                })
        return response


# @main.route('/nodes/chain/', methods=['GET'])
# def get_chain():
#     if blockchain.valid_chain(blockchain.chain):
#         return {'chain': blockchain.chain, 'code': 200}
    
#     else:
#         message = "no valid chain"
#         return {'chain': [], 'message': message, 'code': 204}


# @main.route('/nodes/resolve', methods=['GET'])
# def consensus():
#     msg = f"Our chain is authoritative"
    
#     for node in blockchain.nodes:

#         ip_address = node.get('ip_address')
#         new_chain = requests.get(f"http://{ip_address}/nodes/chain/").json().get('chain')
        
#         if len(new_chain) > len(blockchain.chain):
#             blockchain.replace_chain(new_chain)
        
#             msg = f"Our chain was replaced with chain of {node}"

#     return jsonify(msg), 201

