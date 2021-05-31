import sys
from app import create_app
# from app.main.models import Node

app = create_app()

if __name__=='__main__':
    PORT = sys.argv[1]
    # address = input("Input your address")
    app.config['PORT'] = PORT
    app.run(debug=True, port=PORT)