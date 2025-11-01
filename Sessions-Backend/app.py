from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db, User, Note

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

# Configure CORS - must be before routes
CORS(app, 
     supports_credentials=True,
     resources={r"/*": {"origins": ["http://localhost:4000", "http://localhost:3000"]}},
     allow_headers=["Content-Type"],
     methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"])

# Additional session configuration
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False

# Auth Routes

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        # Validate required fields
        username = data.get('username')
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        
        if not username or not password or not password_confirmation:
            return {'errors': ['Username, password, and password confirmation are required']}, 400
        
        # Check if passwords match
        if password != password_confirmation:
            return {'errors': ['Passwords do not match']}, 400
        
        # Validate username length
        if len(username) < 3:
            return {'errors': ['Username must be at least 3 characters long']}, 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'errors': ['Username already exists']}, 422
        
        try:
            # Create new user
            new_user = User(username=username)
            new_user._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            db.session.add(new_user)
            db.session.commit()
            
            # Set session
            session['user_id'] = new_user.id
            
            return {
                'id': new_user.id,
                'username': new_user.username
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422

class Login(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'errors': ['Username and password are required']}, 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not bcrypt.check_password_hash(user._password_hash, password):
            return {'errors': ['Invalid username or password']}, 401
        
        # Set session
        session['user_id'] = user.id
        
        return {
            'id': user.id,
            'username': user.username
        }, 200

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {}, 401
        
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return {}, 401
        
        return {
            'id': user.id,
            'username': user.username
        }, 200

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {}, 204

class Notes(Resource):
    def get(self):
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query notes for current user with pagination
        paginated_notes = Note.query.filter_by(user_id=user_id).order_by(
            Note.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        # Serialize notes
        notes_list = [note.to_dict() for note in paginated_notes.items]
        
        return {
            'notes': notes_list,
            'total': paginated_notes.total,
            'page': paginated_notes.page,
            'per_page': paginated_notes.per_page,
            'pages': paginated_notes.pages
        }, 200
    
    def post(self):
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        data = request.get_json()
        
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return {'error': 'Title and content are required'}, 400
        
        try:
            # Create new note
            new_note = Note(
                title=title,
                content=content,
                user_id=user_id
            )
            
            db.session.add(new_note)
            db.session.commit()
            
            return new_note.to_dict(), 201
            
        except ValueError as e:
            return {'error': str(e)}, 422

class NoteByID(Resource):
    def get(self, id):
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        # Find note
        note = Note.query.filter_by(id=id, user_id=user_id).first()
        
        if not note:
            return {'error': 'Note not found'}, 404
        
        return note.to_dict(), 200
    
    def patch(self, id):
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        # Find note
        note = Note.query.filter_by(id=id, user_id=user_id).first()
        
        if not note:
            return {'error': 'Note not found'}, 404
        
        data = request.get_json()
        
        try:
            # Update fields if provided
            if 'title' in data:
                note.title = data['title']
            if 'content' in data:
                note.content = data['content']
            
            db.session.commit()
            
            return note.to_dict(), 200
            
        except ValueError as e:
            return {'error': str(e)}, 422
    
    def delete(self, id):
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        # Find note
        note = Note.query.filter_by(id=id, user_id=user_id).first()
        
        if not note:
            return {'error': 'Note not found'}, 404
        
        db.session.delete(note)
        db.session.commit()
        
        return {}, 204

# Register routes
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Notes, '/notes')
api.add_resource(NoteByID, '/notes/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)