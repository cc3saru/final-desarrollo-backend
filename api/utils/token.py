import jwt
from datetime import datetime, timedelta
from app.settings import JWT_SECRET

def encode_token(user, token_type):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'type': int(token_type),
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token. Please log in again.')
    