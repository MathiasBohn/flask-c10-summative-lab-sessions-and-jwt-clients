# The world's best Flask Notes API

A REALLY FUCKING COOL Flask REST API with session-based authentication and CRUD operations for user notes.

## A very simple description

This awesome project provides a secure backend API for managing personal notes. Users can sign up, log in, and perform full CRUD operations on their notes. Each user can only access their own notes, ensuring data privacy and security.

## Installation - for those who dare

1. Install dependencies:
```bash
pipenv install
```

2. Activate virtual environment:
```bash
pipenv shell
```

3. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

4. Seed the database (optional):
```bash
python seed.py
```

## Run the Application
```bash
python app.py
```

The server will start on `http://localhost:5555`

## Run Tests
```bash
pytest
```

For detailed test output:
```bash
pytest -v
```

## API Endpoints - because, I mean, why not

### Authentication Endpoints

#### POST `/signup`
Create a new user account
- **Body**: `{"username": "string", "password": "string", "password_confirmation": "string"}`
- **Success Response**: `201` - Returns user object with id and username
- **Error Response**: `400` - Missing fields or validation error

#### POST `/login`
Log in an existing user
- **Body**: `{"username": "string", "password": "string"}`
- **Success Response**: `200` - Returns user object and sets session cookie
- **Error Response**: `401` - Invalid credentials

#### GET `/check_session`
Check if user is currently logged in
- **Success Response**: `200` - Returns user object if logged in
- **Error Response**: `401` - Not logged in

#### DELETE `/logout`
Log out current user
- **Success Response**: `204` - Session cleared
- **Error Response**: None

### Notes Endpoints (Protected)

All notes endpoints require authentication. Users can only access their own notes.

#### GET `/notes`
Get all notes for current user (supports pagination)
- **Query Parameters**: `page` (default: 1), `per_page` (default: 10)
- **Success Response**: `200` - Returns paginated list of notes
- **Error Response**: `401` - Not authenticated

#### POST `/notes`
Create a new note
- **Body**: `{"title": "string", "content": "string"}`
- **Success Response**: `201` - Returns created note object
- **Error Response**: `400` - Missing required fields, `401` - Not authenticated

#### GET `/notes/:id`
Get a specific note by ID
- **Success Response**: `200` - Returns note object
- **Error Response**: `401` - Not authenticated, `404` - Note not found

#### PATCH `/notes/:id`
Update a note
- **Body**: `{"title": "string", "content": "string"}` (both optional)
- **Success Response**: `200` - Returns updated note object
- **Error Response**: `401` - Not authenticated, `404` - Note not found

#### DELETE `/notes/:id`
Delete a note
- **Success Response**: `204` - Note deleted
- **Error Response**: `401` - Not authenticated, `404` - Note not found

## Test User Credentials

After seeding the database, you can use these credentials:
- Username: `alice` | Password: `password123`
- Username: `bob` | Password: `password123`
- Username: `charlie` | Password: `password123`
- Username: `diana` | Password: `password123`
- Username: `eve` | Password: `password123`

## Project Structure
```
Sessions-Backend/
├── app.py              # Main application file with routes
├── models.py           # Database models (User, Note)
├── config.py           # Configuration settings
├── seed.py             # Database seeding script
├── test_app.py         # Test suite
├── requirements.txt    # Pip dependencies
├── Pipfile             # Pipenv dependencies
└── README.md           # This file
```

## Dependencies (Pipfile)
```
[packages]
Flask = "2.2.2"
Flask-SQLAlchemy = "3.0.3"
Werkzeug = "2.2.2"
marshmallow = "3.20.1"
Faker = "15.3.2"
Flask-Migrate = "4.0.0"
Flask-RESTful = "0.3.9"
importlib-metadata = "6.0.0"
importlib-resources = "5.10.0"
pytest = "7.2.0"
Flask-Bcrypt = "1.0.1"
Flask-Cors = "3.0.10"
sqlalchemy-serializer = "1.4.1"
```

## Features

- ✅ Session-based authentication
- ✅ Password hashing with Bcrypt
- ✅ User registration and login
- ✅ Full CRUD operations for notes
- ✅ Pagination support
- ✅ User data isolation (users can only access their own notes)
- ✅ RESTful API design
- ✅ Comprehensive test suite
- ✅ CORS enabled for frontend integration

## Tech Stack

- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-Bcrypt** - Password hashing
- **Flask-RESTful** - REST API resources
- **Flask-Migrate** - Database migrations
- **Flask-CORS** - Cross-origin resource sharing
- **SQLite** - Database
- **Pytest** - Testing framework

## Security

- Passwords are hashed using Bcrypt before storage
- Session-based authentication with httpOnly cookies
- Route protection - unauthorized users cannot access protected endpoints
- User data isolation - users cannot view or modify other users' data