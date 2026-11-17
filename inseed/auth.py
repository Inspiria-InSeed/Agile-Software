from datetime import datetime
from functools import wraps
from typing import Mapping, Optional

import jwt
from flask import request, jsonify, Response

from config import get_config
from models import User

# Load configuration settings
current_config = get_config()

def generate_token(user_id: int) -> str:
    """
    Generates a new JWT token for a given user ID.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        str: The generated JWT token string.
    """
    payload = {
        'sub': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + current_config.JWT_ACCESS_TOKEN_EXPIRES
    }
    return jwt.encode(payload, current_config.JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token: str) -> Optional[int]:
    """
    Decodes and validates a JWT token.

    Args:
        token: The JWT token string to decode.

    Returns:
        Optional[int]: The user ID if token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, current_config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def token_required(f):
    """
    Decorator to enforce JWT token authentication on API routes.

    Adds the authenticated user object to request.current_user.
    Responds with 401 Unauthorized if token is missing or invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        header_name = current_config.JWT_HEADER_NAME
        header_type = current_config.JWT_HEADER_TYPE

        if header_name in request.headers:
            auth_header = request.headers[header_name]
            parts = auth_header.split()

            if len(parts) == 2 and parts[0] == header_type:
                token = parts[1]

        if not token:
            return jsonify({'message': 'Authentication token is missing'}), 401

        user_id = decode_token(token)
        if user_id is None:
            return jsonify({'message': 'Invalid or expired authentication token'}), 401

        # Database is imported globally within models.py context implicitly by app execution
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'message': 'User associated with token not found'}), 401

        request.current_user = current_user
        return f(*args, **kwargs)

    return decorated

def authenticate_user(credentials: Mapping[str, str]) -> Optional[str]:
    """
    Authenticates a user based on username and password.

    Args:
        credentials: A dictionary containing 'username' and 'password'.

    Returns:
        Optional[str]: Generated JWT token if authentication succeeds, None otherwise.
    """
    username = credentials.get('username')
    password = credentials.get('password')

    if not username or not password:
        return None

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        return generate_token(user.id)

    return None