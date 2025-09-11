#!/usr/bin/env python3
"""
Test UUID generation for database models
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.orm import Session

from app.core.permissions import UserRole
from app.core.security import hash_password
from app.db.session import get_db
from app.models.exam import Exam
from app.models.user import User
from app.models.user_exam import UserExam


def test_uuid_generation():
    """Test that UUID generation works properly"""
    print("🔧 Testing UUID generation in models...")

    # Get database session
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Create a test user
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            role=UserRole.USER,
        )

        db.add(user)
        db.flush()  # Flush to generate UUID but don't commit yet

        print(f"✅ User created with UUID: {user.id}")
        print(f"   UUID type: {type(user.id)}")
        print(f"   UUID length: {len(user.id) if user.id else 'None'}")

        # Create a test exam
        from datetime import date

        exam = Exam(title="Test Exam", date=date.today())

        db.add(exam)
        db.flush()

        print(f"✅ Exam created with UUID: {exam.id}")
        print(f"   UUID type: {type(exam.id)}")
        print(f"   UUID length: {len(exam.id) if exam.id else 'None'}")

        # Create a user-exam association
        user_exam = UserExam(user_id=user.id, exam_id=exam.id, vote=85.5)

        db.add(user_exam)
        db.flush()

        print(f"✅ UserExam created with UUID: {user_exam.id}")
        print(f"   User ID: {user_exam.user_id}")
        print(f"   Exam ID: {user_exam.exam_id}")
        print(f"   Vote: {user_exam.vote}")

        # Test retrieval
        retrieved_user = db.query(User).filter(User.id == user.id).first()
        print(f"✅ User retrieved by UUID: {retrieved_user.email if retrieved_user else 'Not found'}")

        retrieved_exam = db.query(Exam).filter(Exam.id == exam.id).first()
        print(f"✅ Exam retrieved by UUID: {retrieved_exam.title if retrieved_exam else 'Not found'}")

        # Test foreign key relationships
        user_exams = (
            db.query(UserExam)
            .filter(UserExam.user_id == user.id)
            .all()
        )
        print(f"✅ Found {len(user_exams)} user-exam associations")

        # Rollback to not persist test data
        db.rollback()
        print("✅ Test completed successfully - no data persisted")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_uuid_generation()
    sys.exit(0 if success else 1)
