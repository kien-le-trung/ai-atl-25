"""
Quick script to create a test user in the database
"""
import sys
import bcrypt
from app.core.database import SessionLocal
from app.models.user import User

def create_test_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print(f"✅ Test user already exists (ID: {existing_user.id}, Email: {existing_user.email})")
            return existing_user.id

        # Create test user
        password = "test123"  # Simple password for testing
        # Hash password using bcrypt directly
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password,
            is_active=True
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        print(f"✅ Test user created successfully!")
        print(f"   ID: {test_user.id}")
        print(f"   Email: {test_user.email}")
        print(f"   Username: {test_user.username}")
        print(f"   Password: {password}")

        return test_user.id

    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
