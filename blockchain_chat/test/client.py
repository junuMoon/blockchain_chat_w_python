import sys
import socket
import select


def chat_client():
    if (len(sys.argv) < 3):
        print(f"Usage: 'python chat_client.py <hostname> <port>")
        sys.exit()
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((host, port))
    except:
        print("Unable to connect")
        sys.exit()
        
    print('Connected to remote host. You can start sending messages')
    sys.stdout.write('[Me] '); sys.stdout.flush()
    
    while 1:
        socket_list = [sys.stdin, s]
        
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
        
        for sock in ready_to_read:
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print(f"Disconnected from chat server")
                    sys.exit()
                else:
                    sys.stdout.write(str(data.decode()))
                    # print()
                    # sys.stdout.write('[Me] '); sys.stdout.flush()
                    
            else:
                msg = sys.stdin.readline()
                s.send(msg.encode())
                sys.stdout.write('[Me] '); sys.stdout.flush()
                
                
if __name__ == '__main__':
    sys.exit(chat_client())

    

    