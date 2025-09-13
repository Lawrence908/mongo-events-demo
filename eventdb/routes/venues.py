from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

from ..config import Config
from ..models import VenueCreate

bp = Blueprint('venues', __name__)


def get_db():
    """Get database connection"""
    client = MongoClient(Config.MONGODB_URI)
    return client[Config.DB_NAME]


@bp.route('/', methods=['GET'])
def list_venues():
    """List venues with pagination"""
    db = get_db()
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    skip = (page - 1) * per_page
    
    venues = list(db.venues.find().skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for venue in venues:
        venue['_id'] = str(venue['_id'])
    
    return jsonify({
        'venues': venues,
        'page': page,
        'per_page': per_page,
        'total': db.venues.count_documents({})
    })


@bp.route('/', methods=['POST'])
def create_venue():
    """Create a new venue"""
    try:
        data = request.get_json()
        venue_data = VenueCreate(**data)
        
        db = get_db()
        venue_doc = venue_data.model_dump()
        venue_doc['created_at'] = datetime.utcnow()
        
        result = db.venues.insert_one(venue_doc)
        venue_doc['_id'] = str(result.inserted_id)
        
        return jsonify(venue_doc), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<venue_id>', methods=['GET'])
def get_venue(venue_id):
    """Get a single venue"""
    try:
        db = get_db()
        venue = db.venues.find_one({'_id': ObjectId(venue_id)})
        
        if not venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        venue['_id'] = str(venue['_id'])
        return jsonify(venue)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<venue_id>', methods=['PATCH'])
def update_venue(venue_id):
    """Update a venue"""
    try:
        data = request.get_json()
        
        db = get_db()
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.venues.update_one(
            {'_id': ObjectId(venue_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Venue not found'}), 404
        
        # Return updated venue
        venue = db.venues.find_one({'_id': ObjectId(venue_id)})
        venue['_id'] = str(venue['_id'])
        
        return jsonify(venue)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    """Delete a venue"""
    try:
        db = get_db()
        result = db.venues.delete_one({'_id': ObjectId(venue_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Venue not found'}), 404
        
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400
