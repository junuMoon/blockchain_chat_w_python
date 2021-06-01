import sys
import socket
import select
import hashlib

HOST = 'localhost'
SOCKET_LIST = list()
RECV_BUFFER = 4096
PORT = 9009

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(10)

SOCKET_LIST.append(server_socket)

MSG_INDEX = 0

def hash_msg(msg):
    global MSG_INDEX
    hash_id = hashlib.sha256(f"{MSG_INDEX}{msg}".encode()).hexdigest()
    msg_set = (hash_id, msg)
    MSG_INDEX += 1
    return msg_set

while 1:
    
    r, w, e = select.select(SOCKET_LIST, [], [])
    
    for sock in r:
        if sock == server_socket:
            client, addr = server_socket.accept()
            
            SOCKET_LIST.append(client)
            conn_msg = f"Client [{addr}] connected"
            msg = hash_msg(conn_msg)
            print(f"HASH: {msg[0]}\nMessage: {msg[1]}")
            
            
        else:
            try:
                data = sock.recv(RECV_BUFFER).decode()
                if data:
                    raw_msg = f"[{sock.getpeername()}]: {data}"
                    msg = hash_msg(raw_msg)
                    print(f"HASH: {msg[0]}\n{msg[1]}")

                else:
                    if sock in SOCKET_LIST:
                        SOCKET_LIST.remove(sock)
                        disconn_msg = f"Client [{sock.getpeername()}] left the chat room"
                        msg = hash_msg(disconn_msg)
                        print(f"HASH: {msg[0]}\nMessage: {msg[1]}")
            except:
                if sock in SOCKET_LIST:
                    SOCKET_LIST.remove(sock)
                    disconn_msg = f"Client [{sock.getpeername()}] left the chat room"
                    msg = hash_msg(disconn_msg)
                    print(f"HASH: {msg[0]}\nMessage: {msg[1]}")
                    
                continue

server_socket.close()
    
