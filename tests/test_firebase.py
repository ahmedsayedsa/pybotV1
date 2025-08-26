import pytest
from src.config.firebase import init_firebase
from src.repositories.firestore_repo import FirestoreRepository

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        db = init_firebase()
        assert db is not None
        print("Firebase connection test passed")
    except Exception as e:
        pytest.fail(f"Firebase connection failed: {str(e)}")

def test_firestore_operations():
    """Test basic Firestore operations"""
    try:
        repo = FirestoreRepository()
        
        # Test collection access
        users = repo.users_collection
        assert users is not None
        
        print("Firestore operations test passed")
    except Exception as e:
        pytest.fail(f"Firestore operations failed: {str(e)}")