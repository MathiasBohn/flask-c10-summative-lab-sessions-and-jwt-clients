from app import app, db
from models import User, Note
from flask_bcrypt import Bcrypt
from faker import Faker
from datetime import datetime, timedelta
import random

bcrypt = Bcrypt()
fake = Faker()

def seed_database():
    with app.app_context():
        print("Clearing database...")
        Note.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("Creating users...")
        users = []
        
        # Create 5 users with simple passwords
        usernames = ['alice', 'bob', 'charlie', 'diana', 'eve']
        
        for username in usernames:
            password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(
                username=username,
                _password_hash=password_hash
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        print("Creating notes...")
        notes = []
        
        # Create 3-7 notes for each user
        for user in users:
            num_notes = random.randint(3, 7)
            
            for i in range(num_notes):
                # Create note with random past date
                days_ago = random.randint(1, 30)
                note = Note(
                    title=fake.sentence(nb_words=4).rstrip('.'),
                    content=fake.paragraph(nb_sentences=5),
                    user_id=user.id,
                    created_at=datetime.utcnow() - timedelta(days=days_ago)
                )
                notes.append(note)
                db.session.add(note)
        
        db.session.commit()
        print(f"Created {len(notes)} notes")
        
        print("Database seeded successfully!")
        print("\nTest credentials:")
        print("Username: alice | Password: password123")
        print("Username: bob | Password: password123")
        print("Username: charlie | Password: password123")
        print("Username: diana | Password: password123")
        print("Username: eve | Password: password123")

if __name__ == '__main__':
    seed_database()