from functools import reduce

import requests
from flask import (current_app, g, redirect, render_template, request, session,
                   url_for)
from sqlalchemy.sql.expression import func

from .. import db
from . import main
from .models import Block, Node, Transaction
from .utils import generate_genesis_block, valid_chain

CONN_NODES_NUM = current_app.config['CONN_NODES_NUM']
CONN_NODES = set() #TODO: collections.deque
CONN_NODES_SEAT = CONN_NODES_NUM - len(CONN_NODES)
MY_IP = ''
MY_ADDRESS = ''
    

@main.route('/', methods=['GET'])
def index():
    if valid_chain().get('valid'):
        hash_id = request.args.get('hash_id')
        blocks = [b.previous_hash for b in db.session.query(Block).order_by(Block.index.desc()).all()]
        if hash_id:
            block = db.session.query(Block).filter(Block.previous_hash == hash_id).first()
            transactions = block.transactions
            
        else:
            transactions = db.session.query(Transaction).filter(Transaction.added_to_block == 0).all()

        return render_template('index.html', 
                            blocks=blocks,
                            target_block_hash = hash_id,
                            transactions=transactions,
                            nodes=CONN_NODES,
                            ip_address=MY_IP,
                            address=MY_ADDRESS)


@main.route('/blocks/mine/', methods=['GET'])
def mine():
    last_block = db.session.query(Block).order_by(Block.index.desc()).first()
    
    if not last_block:
        generate_genesis_block(MY_ADDRESS)
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
        generate_genesis_block(MY_ADDRESS)
        print("genesis block created.")
        return redirect(url_for('.index'))
        
    if request.method == 'GET':
        address_list = [node.address for node in db.session.query(Node).all()]
        return render_template('new_transaction.html', data=address_list)
    
    elif request.method == 'POST':
        sender_address = MY_ADDRESS
        recipient_address = request.form['recipient-address']
        assert sender_address != recipient_address
        
        amount = int(request.form['amount'])
        tx_inputs = db.session.query(Transaction)\
            .filter(Transaction.tx_outputs == None)\
                .filter(Transaction.recipient==sender_address).all()
        
        new_tx = Transaction(recipient=recipient_address,
                             amount=amount,
                             tx_inputs=tx_inputs
                             )
        
        balance = reduce(lambda x, y: x+y, [t.amount for t in tx_inputs]) - amount #FIXME: session error
        balance_tx = balance_transaction(sender_address, balance, tx_inputs)
        
        db.session.add(new_tx)
        db.session.add(balance_tx)
        db.session.commit()
        
        return redirect(url_for('.index'))

def balance_transaction(sender, balance, tx_inputs):
    balance_tx = Transaction(
        recipient = sender,
        amount = balance,
        tx_inputs = tx_inputs
    )
    return balance_tx

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
    

@main.route('/nodes/connect/', methods=['GET', 'POST'])
def connect_nodes():
    if request.method == 'GET':
        # while CONN_NODES_SEAT: #FIXME: concurrency
        ips = [node.ip_address for node in CONN_NODES]
        ips.append(MY_IP)
        nodes = db.session.query(Node).filter(Node.ip_address.not_in(ips)).order_by(func.random()).limit(CONN_NODES_SEAT).all()
        
        nodes = set(nodes) - CONN_NODES
        
        for node in nodes:
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
            print('from', new_node)
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


@main.route('/nodes/chain', methods=['GET'])
def get_chain():
    try:
        inspection = valid_chain()
        if inspection.get('valid'):
            return inspection.get('chain')
        else:
            return "Invalid Chain"
    except KeyError:
        print(KeyError)
        return "Error occurred"
    

@main.route('/nodes/resolve', methods=['GET'])
def consensus():
    chain = db.session.query(Block).order_by(Block.id.asc()).all()
    for node in CONN_NODES:
        try:
            response = requests.get(f"http://{node.ip_address}/nodes/chain")
            new_chain = response.json().get('chain')

        except AttributeError:
            msg = f"{node.ip_address} chain is invalid"
            continue
        
        if len(chain) < len(new_chain):
            db.session.query(Block).delete()
            db.session.add_all(new_chain)
            db.session.commit()
            
            msg = f"Our chain was replaced with chain of {node}"
            
    return redirect(url_for('.index'))
