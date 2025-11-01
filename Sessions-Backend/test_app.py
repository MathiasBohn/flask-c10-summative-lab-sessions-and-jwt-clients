import pytest
from app import app, db
from models import User, Note
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Setup and Teardown
@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def test_user(client):
    """Create a test user and return the ID."""
    with app.app_context():
        password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(username='testuser', _password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Store the ID before leaving the context
    return user_id


@pytest.fixture
def logged_in(client, test_user):
    """Login the test user."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user  # test_user is now just an ID
    return client


# Authentication Tests
def test_signup_works(client):
    """Test user can sign up."""
    response = client.post('/signup', json={
        'username': 'newuser',
        'password': 'pass123',
        'password_confirmation': 'pass123'
    })
    assert response.status_code == 201


def test_login_works(client, test_user):
    """Test user can login."""
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200


def test_login_fails_with_wrong_password(client, test_user):
    """Test login fails with wrong password."""
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401


def test_check_session_works(logged_in):
    """Test check_session returns user when logged in."""
    response = logged_in.get('/check_session')
    assert response.status_code == 200


def test_logout_works(logged_in):
    """Test logout clears session."""
    response = logged_in.delete('/logout')
    assert response.status_code == 204


# Authorization Tests
def test_cannot_access_notes_when_not_logged_in(client):
    """Test unauthorized users cannot access notes."""
    response = client.get('/notes')
    assert response.status_code == 401


def test_cannot_create_note_when_not_logged_in(client):
    """Test unauthorized users cannot create notes."""
    response = client.post('/notes', json={
        'title': 'Test',
        'content': 'Test'
    })
    assert response.status_code == 401


# CRUD Tests
def test_create_note(logged_in):
    """Test creating a note."""
    response = logged_in.post('/notes', json={
        'title': 'My Note',
        'content': 'Note content'
    })
    assert response.status_code == 201
    assert response.get_json()['title'] == 'My Note'


def test_get_all_notes(logged_in):
    """Test getting all notes."""
    # Create a note first
    logged_in.post('/notes', json={'title': 'Test', 'content': 'Content'})
    
    response = logged_in.get('/notes')
    assert response.status_code == 200
    assert 'notes' in response.get_json()


def test_update_note(logged_in):
    """Test updating a note."""
    # Create a note
    create_response = logged_in.post('/notes', json={
        'title': 'Original',
        'content': 'Original content'
    })
    note_id = create_response.get_json()['id']
    
    # Update it
    response = logged_in.patch(f'/notes/{note_id}', json={
        'title': 'Updated'
    })
    assert response.status_code == 200
    assert response.get_json()['title'] == 'Updated'


def test_delete_note(logged_in):
    """Test deleting a note."""
    # Create a note
    create_response = logged_in.post('/notes', json={
        'title': 'To Delete',
        'content': 'Will be deleted'
    })
    note_id = create_response.get_json()['id']
    
    # Delete it
    response = logged_in.delete(f'/notes/{note_id}')
    assert response.status_code == 204


def test_user_can_only_see_own_notes(client):
    """Test users can only access their own notes."""
    # Create user 1 and note
    with app.app_context():
        hash1 = bcrypt.generate_password_hash('pass1').decode('utf-8')
        user1 = User(username='user1', _password_hash=hash1)
        db.session.add(user1)
        db.session.commit()
        user1_id = user1.id
        
        note = Note(title='User1 Note', content='Content', user_id=user1_id)
        db.session.add(note)
        db.session.commit()
        note_id = note.id
    
    # Create user 2
    with app.app_context():
        hash2 = bcrypt.generate_password_hash('pass2').decode('utf-8')
        user2 = User(username='user2', _password_hash=hash2)
        db.session.add(user2)
        db.session.commit()
        user2_id = user2.id
    
    # Login as user 2
    with client.session_transaction() as sess:
        sess['user_id'] = user2_id
    
    # Try to access user 1's note
    response = client.get(f'/notes/{note_id}')
    assert response.status_code == 404


def test_pagination_works(logged_in):
    """Test pagination returns correct number of notes."""
    # Create 5 notes
    for i in range(5):
        logged_in.post('/notes', json={
            'title': f'Note {i}',
            'content': f'Content {i}'
        })
    
    # Get with pagination
    response = logged_in.get('/notes?page=1&per_page=3')
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data['notes']) == 3
    assert data['total'] == 5