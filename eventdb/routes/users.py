from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

from ..config import Config
from ..models import UserCreate

bp = Blueprint('users', __name__)


def get_db():
    """Get database connection"""
    client = MongoClient(Config.MONGODB_URI)
    return client[Config.DB_NAME]


@bp.route('/', methods=['GET'])
def list_users():
    """List users with pagination"""
    db = get_db()
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    skip = (page - 1) * per_page
    
    users = list(db.users.find().skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for user in users:
        user['_id'] = str(user['_id'])
    
    return jsonify({
        'users': users,
        'page': page,
        'per_page': per_page,
        'total': db.users.count_documents({})
    })


@bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        user_data = UserCreate(**data)
        
        db = get_db()
        user_doc = user_data.model_dump()
        user_doc['created_at'] = datetime.utcnow()
        
        result = db.users.insert_one(user_doc)
        user_doc['_id'] = str(result.inserted_id)
        
        return jsonify(user_doc), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a single user"""
    try:
        db = get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user['_id'] = str(user['_id'])
        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<user_id>', methods=['PATCH'])
def update_user(user_id):
    """Update a user"""
    try:
        data = request.get_json()
        
        db = get_db()
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'User not found'}), 404
        
        # Return updated user
        user = db.users.find_one({'_id': ObjectId(user_id)})
        user['_id'] = str(user['_id'])
        
        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        db = get_db()
        result = db.users.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'User not found'}), 404
        
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400
