from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

# SQLAlchemy naming convention for constraints
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    # Serialization rules
    serialize_rules = ('-_password_hash', '-notes.user')
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    
    # Relationship
    notes = db.relationship('Note', back_populates='user', cascade='all, delete-orphan')
    
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username is required")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return username
    
    def __repr__(self):
        return f'<User {self.username}>'


class Note(db.Model, SerializerMixin):
    __tablename__ = 'notes'
    
    # Serialization rules
    serialize_rules = ('-user.notes',)
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship
    user = db.relationship('User', back_populates='notes')
    
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title is required")
        if len(title) < 1:
            raise ValueError("Title cannot be empty")
        return title
    
    @validates('content')
    def validate_content(self, key, content):
        if not content:
            raise ValueError("Content is required")
        return content
    
    def __repr__(self):
        return f'<Note {self.title}>'