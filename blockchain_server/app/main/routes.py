from flask import redirect, render_template, request, url_for, session, current_app, g

import requests

from sqlalchemy.sql.expression import func

from .. import db
from .models import Block, Transaction, Node
from . import main

CONN_NODES_NUM = 2
CONN_NODES = set()
CONN_NODES_SEAT = CONN_NODES_NUM - len(CONN_NODES)
MY_IP = ''
MY_ADDRESS = ''

def generate_genesis_block():
    if not db.session.query(Block).first():
        
        block = Block(
            index=0,
            miner=session['node-address']
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
    

@main.route('/', methods=['GET'])
def index():
    hash_id = request.args.get('hash_id')
    blocks = [b.previous_hash for b in db.session.query(Block).order_by(Block.index.desc()).all()]
    if hash_id:
        b = db.session.query(Block).filter(Block.previous_hash == hash_id).first()
        transactions = [tx.to_dict() for tx in b.transactions]
        
    else:
        transactions = db.session.query(Transaction).filter(Transaction.added_to_block == 0).all()
    
    #TODO: valid chain

    return render_template('index.html', 
                           blocks=blocks,
                           target_block_hash = hash_id,
                           transactions=transactions,
                           nodes=CONN_NODES, #TODO use flask g
                           ip_address=MY_IP,
                           address=MY_ADDRESS)


@main.route('/blocks/mine/', methods=['GET'])
def mine():
    last_block = db.session.query(Block).order_by(Block.index.desc()).first()
    
    if not last_block:
        generate_genesis_block()
        return redirect(url_for('.index'))
        
    _hash, _nonce = Block._proof_of_work(last_block)
    
    new_block = Block(previous_hash=_hash,
                      miner=MY_ADDRESS,
                      nonce=_nonce)
    
    txs = Transaction.txs_to_block(new_block)
        
    new_block.transactions = txs
    new_block.index = last_block.index + 1
    db.session.add_all(txs)
    db.session.add(new_block)
    db.session.commit()

    return redirect(url_for('.index', target_block_hash=new_block.previous_hash))


@main.route('/transactions/new', methods=['GET', 'POST'])
def submit_transaction():
    last_block = db.session.query(Block).order_by(Block.index.desc()).first()
    if not last_block:
        generate_genesis_block()
        print("genesis block created.")
        return redirect(url_for('.index'))
        
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
    

@main.before_app_request
def node_session():
    global MY_IP
    global MY_ADDRESS
    
    if MY_IP: # check if session has ip address
        if request.endpoint == 'main.node_register':
            return redirect(url_for('.index'))
        
    else:
        node = db.session.query(Node).filter(Node.ip_address=='127.0.0.1:'+current_app.config['PORT']).first()
        if node:
            MY_IP = node.ip_address
            MY_ADDRESS = node.address
            if request.endpoint == 'main.node_register':
                return redirect(url_for('.index'))
                
        else:
            if request.endpoint != 'main.node_register':
                return redirect(url_for('.node_register'))
            
    
@main.route('/nodes/register', methods=['GET', 'POST'])
def node_register():
    if request.method == 'GET':
        return render_template('nodes_register.html')
        
    elif request.method == 'POST':
        address = request.form['address']
        node = Node(ip_address='127.0.0.1:'+current_app.config['PORT'], address=address)
        db.session.add(node)
        db.session.commit()

        return redirect(url_for('.index'))
    
import time
@main.route('/nodes/connect/', methods=['GET', 'POST'])
def connect_nodes():
    if request.method == 'GET':
        # while CONN_NODES_SEAT: #FIXME: concurrency
        nodes = db.session.query(Node).filter(Node.ip_address!=MY_IP).order_by(func.random()).limit(CONN_NODES_SEAT).all()
        
        nodes = set(nodes) - CONN_NODES
        
        for node in nodes:
            print(node.ip_address)
            try:
                #TODO: asynchronous connection
                #TODO: iter until get 5 connected nodes
                #TODO: random walk
                req = requests.post(f"http://{node.ip_address}/nodes/accept/",
                            json={
                                'ip_address': MY_IP,
                                'address': MY_ADDRESS
                            })
            except Exception as e:
                message = f"Connection to {node.ip_address} has failed"
                print(e, message) #TODO: HTTPConnectionPool error handling
                continue
            
        return redirect(url_for('.index'))
                
    if request.method == 'POST':
        status = request.get_json().get('status')
        if status == 0: #TODO: status zero -> out of seat
            message = 'declined: out of seat'
            return message
        
        elif status == 1:
            try:
                values = request.get_json()
                new_node_ip_address = values.get('ip_address')
                new_node = db.session.query(Node).filter(Node.ip_address==new_node_ip_address).first()
                CONN_NODES.add(new_node)
                return f'connection between {new_node_ip_address}'   
            except Exception as e:
                print("wrong", e) #TODO: what wrong
                return "need handling"
        
        # elif status == 2:
        #     values = request.get_json()
        #     ip_address = values.get('ip_address')
        #     for node in CONN_NODES:
        #         if node.ip_address == ip_address:
        #             CONN_NODES.remove(node)
                    
        #     return 'dummy string2'
            
                
# status 0: no seat
# status 1: good
# status 2: close server
@main.route('/nodes/accept/', methods=['POST'])
def accept_node():
    try:
        values = request.get_json()
        # status = values.get('status')
        new_node_address = values.get('address')
        new_node_ip_address = values.get('ip_address')
        dict_4_response_json = {
                        'ip_address': MY_IP,
                        'address': MY_ADDRESS,
                        }
        
        if not CONN_NODES_SEAT:
            dict_4_response_json['status'] = 0
            dict_4_response_json['message'] = f"{MY_IP} is out of seat."
            response = requests.post(f"http://{new_node_ip_address}/nodes/connect/",
                                     json=dict_4_response_json)
            return dict_4_response_json['message']
        
        else:
            new_node = db.session.query(Node).filter(Node.ip_address==new_node_ip_address).first()
            if not new_node:
                new_node = Node(ip_address=new_node_ip_address, address=new_node_address)
                db.session.add(new_node)
                db.session.commit()
            CONN_NODES.add(new_node) #FIXME: not db instance -> 
            
            dict_4_response_json['status'] = 1
            dict_4_response_json['message'] = f"Connections between {MY_IP} - {new_node_ip_address} has been established."
            response = requests.post(f"http://{new_node_ip_address}/nodes/connect/",
                                     json=dict_4_response_json)
            return dict_4_response_json['message']
    
    except Exception as e:
        print(e)
        return f"Error occurred: {e}"

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

