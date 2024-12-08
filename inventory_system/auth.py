from flask import Blueprint, jsonify, request, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import re

from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

# Email validation pattern via RegEx
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$')

def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email))

# Login required decorator
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Registration route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'password', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Email format validation
    if not is_valid_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        password=hashed_password,
        email=data['email'].lower()  # Store email in lowercase for consistency
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.form if request.form else request.get_json()
    
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing credentials'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password, data['password']):
        #remove all preexisting session data
        session.clear()
        session.permanent = True
        
        #after clearing the session, the user id of the authenticated user is stored in the session. 
        session['user_id'] = user.id
        return jsonify({'message': 'Logged in successfully'}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Logout route
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Login page route
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')