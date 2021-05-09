from flask import Flask, request
from flask.templating import render_template
from werkzeug.utils import redirect

from .blockchain import Blockchain


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/', methods=["GET", "POST"])
def index():
    sessions = request.post('/nodes/register')
    return render_template('index.html')


@app.route('/blocks/{hash}', method=['get'])
def index():
    return render_template('index.html')


@app.route('blocks/mine', methods=["GET"])
def mine():
    return redirect('blocks', block_hash='new_block_hash')


@app.route('/transactions/new', methods=["POST"])
def submit_transaction():
    redirect('blocks', block_hash='selected_block_hash')


@app.route('/nodes/register', methods=["GET"])
def node_register():
    return redirect('home')



