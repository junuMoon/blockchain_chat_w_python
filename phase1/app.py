from flask import Flask
from flask.templating import render_template

from .blockchain import Blockchain


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/mine', methods=["GET", "POST"])
def mine():
    return


@app.route('/transactions/new', methods=["GET", "POST"])
def new_transaction():
    return


@app.route('/transactions/', methods=["GET", "POST"])
def get_transactions():
    return


@app.route('/nodes/register', methods=["GET", "POST"])
def node_register():
    return


@app.route('/nodes/resolve', methods=["GET", "POST"])
def node_resolve():
    return

