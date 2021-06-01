import os
from flask import Flask, render_template, session, url_for, redirect, request
from flask_socketio import SocketIO, emit
from blockchain import HashedMessage
from flask import Blueprint

bp = Blueprint('main', __name__, url_prefix='/')

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'root'
# socketio = SocketIO(app)

USER_NO = 1
hash_id = ''

@bp.before_request 
def before_request():
    global USER_NO
    if 'session' in session and 'user-id' in session:
        pass
    else:
        session['session'] = os.urandom(24)
        session['user_id'] = 'user'+str(USER_NO)
        USER_NO += 1

@bp.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('main.html')
    else:
        try:
            username = request.form.get('username')
            session['username'] = username
            return redirect(url_for('chat'))
        except:
            print('error ocurred')

@bp.route('/chat')
def chat():
    return render_template('session.html')

@socketio.on('connect', namespace='/chat/socket')
def connect():
    
    global hash_id
    
    data = 'entered to chat room'
    
    h_msg = HashedMessage(username=session['username'], data=data, previous_hash=hash_id)
    d_msg = h_msg.as_dict()
    hash_id = d_msg['hash']
    
    emit("response", {'hash_id': d_msg['hash'],
                      'timestamp': d_msg['timestamp'],
                      'username': d_msg['username'],
                      'data': d_msg['data'],
                      },
         broadcast=True)
    

@socketio.on("requests", namespace='/chat/socket')
def requests(message):
    
    global hash_id
        
    h_msg = HashedMessage(username=session['username'], data=message['data'], previous_hash=hash_id)
    d_msg = h_msg.as_dict()
    hash_id = d_msg['hash']
    
    emit("response", {'hash_id': d_msg['hash'],
                      'timestamp': d_msg['timestamp'],
                      'username': d_msg['username'],
                      'data': d_msg['data'],
                      },
         broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)