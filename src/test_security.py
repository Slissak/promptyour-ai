from backend.app.core.security import get_password_hash
try:
    print("Hashing 'password123'...")
    hash = get_password_hash("password123")
    print(f"Success: {hash}")
except Exception as e:
    print(f"Error: {e}")
