from werkzeug.security import generate_password_hash,check_password_hash

def get_password_hash(password):
    return generate_password_hash(str(password))

def verify_password(plain_password,hashed_password):
    return check_password_hash(str(plain_password),str(hashed_password))

