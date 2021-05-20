import sys
from blockchain_server import create_app

PORT = sys.argv[1]

app = create_app()

if __name__ == '__main__':  # works if run directly this program
    app.run(debug=True, host='127.0.0.1', port=PORT)
