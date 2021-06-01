from flask import redirect, render_template, request, url_for, session, current_app, g

import requests

from sqlalchemy.sql.expression import func

from .. import db
from .models import Block, Transaction, Node
from . import main



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
    try:
        ip_address=session['node-ip-address']
        address=session['node-address']
    except KeyError:
        return redirect(url_for('.node_register'))
    
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
                           nodes=CONNECT_NODES, #TODO use flask g
                           ip_address=ip_address,
                           address=address)


@main.route('/blocks/mine/', methods=['GET'])
def mine():
    last_block = db.session.query(Block).order_by(Block.index.desc()).first()
    
    if not last_block:
        generate_genesis_block()
        return redirect(url_for('.index'))
        
    _hash, _nonce = Block._proof_of_work(last_block)
    
    new_block = Block(previous_hash=_hash,
                      miner=session['node-address'],
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
    

CONNECT_NODES_NUM = 5
CONNECT_NODES = list()
CONNECT_NODES_SEAT = CONNECT_NODES_NUM - len(CONNECT_NODES)

g['CONNECT_NODES_NUM'] = 5
g['CONNECT_NODES'] = [[] for i in range(g['CONNECT_NODES_NUM'])]

@main.before_app_request
def node_session():
    if session.get('node-ip-address'): # check if session has ip address
        pass
    
    elif not session.get('node-ip-address') and request.endpoint != 'main.node_register': # check if db has ip address and store it on session
        node = db.session.query(Node).filter(Node.ip_address=='127.0.0.1:'+current_app.config['PORT']).first()
        if node:
            session['node-ip-address'] = node.ip_address
            session['node-address'] = node.address
        else:
            return redirect(url_for('.node_register'))

    elif not session.get('node-ip-address') and request.endpoint == 'main.node_register': # redirect to node register
        pass
    
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
    

@main.route('/nodes/connect/', methods=['GET', 'POST'])
def connect_nodes():
    if request.method == 'GET':
    
        nodes = db.session.query(Node).filter(Node.ip_address!=session['node-ip-address']).order_by(func.random()).limit(CONNECT_NODES_SEAT).all()
        for node in nodes:
            try:
                #TODO: asynchronous connection
                req = requests.post(f"http://{node.ip_address}/nodes/accept/",
                            json={
                                'ip_address': session['node-ip-address'],
                                'address': session['node-address']
                            })
                print(req.request.url)
            except Exception as e:
                message = f"Connection to {node.ip_address} has failed"
                print(e, message) #TODO: HTTPConnectionPool error handling
                continue
        
        return redirect(url_for('.index'))
                
    elif request.method == 'POST':
        if request.get_json().get('status') == 0: #TODO: status zero -> out of seat
            message = ''
        
        elif request.get_json().get('status') == 1:
            try:
                values = request.get_json()
                
                new_node_ip_address = values.get('ip_address')
                new_node = db.session.query(Node).filter(Node.ip_address==new_node_ip_address).first()
                CONNECT_NODES.append(new_node)
                return 'dummy string'
            except Exception as e:
                print("wrong", e) #TODO: what wrong
                return "need handling"
            
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
                        'ip_address': session['node-ip-address'],
                        'address': session['node-address'],
                        }
        
        if not CONNECT_NODES_SEAT:
            dict_4_response_json['status'] = 0
            dict_4_response_json['message'] = f"{session['node-ip-address']} is out of seat."
            response = requests.post(f"http://{new_node_ip_address}/nodes/connect/",
                                     json=dict_4_response_json)
            return dict_4_response_json['message']
        
        else:
            new_node = db.session.query(Node).filter(Node.ip_address==new_node_ip_address).first()
            if not new_node:
                new_node = Node(ip_address=new_node_ip_address, address=new_node_address)
                db.session.add(new_node)
                db.session.commit()
            CONNECT_NODES.append(new_node)
            
            dict_4_response_json['status'] = 1
            dict_4_response_json['message'] = f"Connections between {session['node-ip-address']} - {new_node_ip_address} has been established."
            response = requests.post(f"http://{new_node_ip_address}/nodes/connect/",
                                     json=dict_4_response_json)
            return dict_4_response_json['message']
    
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

