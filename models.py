#models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<ChatHistory {self.id} {self.role} {self.content}>'