from blockchain_server import db


class Example(db.Model):
    
    __tablename__='examples'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(100), nullable=False)
    
    