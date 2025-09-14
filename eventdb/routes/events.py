from flask import Blueprint, request, jsonify, render_template
from pymongo import MongoClient, TEXT
from bson import ObjectId
from datetime import datetime
import json

from ..config import Config
from ..models import EventCreate, EventUpdate, EventsNearbyQuery, TextSearchQuery

bp = Blueprint('events', __name__)


def get_db():
    """Get database connection"""
    client = MongoClient(Config.MONGODB_URI)
    return client[Config.DB_NAME]


@bp.route('/', methods=['GET'])
def list_events():
    """List events with pagination"""
    db = get_db()
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    skip = (page - 1) * per_page
    
    events = list(db.events.find().skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for event in events:
        event['_id'] = str(event['_id'])
        event['venueId'] = str(event['venueId'])
    
    return jsonify({
        'events': events,
        'page': page,
        'per_page': per_page,
        'total': db.events.count_documents({})
    })


@bp.route('/', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        event_data = EventCreate(**data)
        
        db = get_db()
        event_doc = event_data.model_dump()
        event_doc['created_at'] = datetime.utcnow()
        
        result = db.events.insert_one(event_doc)
        event_doc['_id'] = str(result.inserted_id)
        event_doc['venueId'] = str(event_doc['venueId'])
        
        return jsonify(event_doc), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get a single event"""
    try:
        db = get_db()
        event = db.events.find_one({'_id': ObjectId(event_id)})
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        event['_id'] = str(event['_id'])
        event['venueId'] = str(event['venueId'])
        
        return jsonify(event)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<event_id>', methods=['PATCH'])
def update_event(event_id):
    """Update an event"""
    try:
        data = request.get_json()
        event_data = EventUpdate(**data)
        
        db = get_db()
        update_data = {k: v for k, v in event_data.model_dump().items() if v is not None}
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.events.update_one(
            {'_id': ObjectId(event_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Event not found'}), 404
        
        # Return updated event
        event = db.events.find_one({'_id': ObjectId(event_id)})
        event['_id'] = str(event['_id'])
        event['venueId'] = str(event['venueId'])
        
        return jsonify(event)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        db = get_db()
        result = db.events.delete_one({'_id': ObjectId(event_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Event not found'}), 404
        
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/search', methods=['GET'])
def search_events():
    """Text search events"""
    try:
        query = TextSearchQuery(**request.args)
        
        db = get_db()
        cursor = db.events.find(
            {'$text': {'$search': query.q}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).limit(query.limit)
        
        events = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
            event['venueId'] = str(event['venueId'])
        
        return jsonify({
            'events': events,
            'query': query.q,
            'count': len(events)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/nearby', methods=['GET'])
def get_nearby_events():
    """Get nearby events using geospatial query"""
    try:
        # Extract parameters with proper names
        lng = float(request.args.get('lng', 0))
        lat = float(request.args.get('lat', 0))
        radius = float(request.args.get('radius', 10))
        limit = int(request.args.get('limit', 50))
        
        db = get_db()
        
        # Aggregation pipeline for nearby events
        pipeline = [
            {
                '$lookup': {
                    'from': 'venues',
                    'localField': 'venueId',
                    'foreignField': '_id',
                    'as': 'venue'
                }
            },
            {'$unwind': '$venue'},
            {
                '$geoNear': {
                    'near': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    'distanceField': 'distanceMeters',
                    'spherical': True,
                    'key': 'venue.location',
                    'maxDistance': radius * 1000
                }
            },
            {'$limit': limit}
        ]
        
        events = list(db.events.aggregate(pipeline))
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
            event['venueId'] = str(event['venueId'])
            if 'venue' in event:
                event['venue']['_id'] = str(event['venue']['_id'])
        
        return jsonify({
            'events': events,
            'query': {
                'lng': lng,
                'lat': lat,
                'radius': radius
            },
            'count': len(events)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def get_nearby_events_geojson():
    """Get nearby events as GeoJSON for map display"""
    try:
        # Extract parameters with proper names
        lng = float(request.args.get('lng', 0))
        lat = float(request.args.get('lat', 0))
        radius = float(request.args.get('radius', 10))
        limit = int(request.args.get('limit', 50))
        
        db = get_db()
        
        # Aggregation pipeline for nearby events with GeoJSON output
        pipeline = [
            {
                '$lookup': {
                    'from': 'venues',
                    'localField': 'venueId',
                    'foreignField': '_id',
                    'as': 'venue'
                }
            },
            {'$unwind': '$venue'},
            {
                '$geoNear': {
                    'near': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    'distanceField': 'distanceMeters',
                    'spherical': True,
                    'key': 'venue.location',
                    'maxDistance': radius * 1000
                }
            },
            {'$limit': limit}
        ]
        
        events = list(db.events.aggregate(pipeline))
        
        # Convert to GeoJSON format
        geojson = {
            'type': 'FeatureCollection',
            'features': []
        }
        
        for event in events:
            feature = {
                'type': 'Feature',
                'geometry': event['venue']['location'],
                'properties': {
                    'id': str(event['_id']),
                    'title': event['title'],
                    'description': event.get('description', ''),
                    'datetime': event['datetime'].isoformat(),
                    'price': event.get('price'),
                    'seatsAvailable': event['seatsAvailable'],
                    'distanceMeters': event['distanceMeters'],
                    'venue': {
                        'name': event['venue']['name'],
                        'address': event['venue']['address']
                    }
                }
            }
            geojson['features'].append(feature)
        
        return jsonify(geojson)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
