from app.utils.security import hash_password, verify_password

password = "harsh@123"

hashed = hash_password(password)

print("Original Password:", password)
print("Hashed Password:", hashed)

print("Correct Password:", verify_password("harsh@123", hashed))
print("Wrong Password:", verify_password("wrongpassword", hashed))