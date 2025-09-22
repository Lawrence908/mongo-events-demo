from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import json

from ..config import Config

bp = Blueprint('admin', __name__)


def get_db():
    """Get database connection"""
    client = MongoClient(Config.MONGODB_URI)
    return client[Config.DB_NAME]


@bp.route('/explain', methods=['POST'])
def explain_query():
    """Explain query execution for performance analysis"""
    try:
        data = request.get_json()
        query_id = data.get('query_id')
        
        if not query_id:
            return jsonify({'error': 'query_id is required'}), 400
        
        db = get_db()
        
        # Define saved queries
        saved_queries = {
            'text_search': {
                'collection': 'events',
                'query': {'$text': {'$search': 'music'}},
                'options': {'score': {'$meta': 'textScore'}}
            },
            'geo_nearby': {
                'collection': 'events',
                'pipeline': [
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
                                'coordinates': [-74.0060, 40.7128]
                            },
                            'distanceField': 'distanceMeters',
                            'spherical': True,
                            'key': 'venue.location',
                            'maxDistance': 5000
                        }
                    }
                ]
            },
            'venue_events': {
                'collection': 'events',
                'query': {'venueId': ObjectId()},
                'options': {'sort': [('datetime', 1)]}
            },
            'user_tickets': {
                'collection': 'tickets',
                'query': {'userId': ObjectId()},
                'options': {'sort': [('purchasedAt', -1)]}
            }
        }
        
        if query_id not in saved_queries:
            return jsonify({'error': 'Query not found'}), 404
        
        query_config = saved_queries[query_id]
        collection = db[query_config['collection']]
        
        # Execute query with explain
        if 'pipeline' in query_config:
            # Aggregation pipeline
            result = list(collection.aggregate(
                query_config['pipeline'],
                explain=True
            ))
        else:
            # Find query
            result = collection.find(
                query_config['query'],
                query_config.get('options', {})
            ).explain()
        
        return jsonify({
            'query_id': query_id,
            'explain': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/indexes', methods=['GET'])
def list_indexes():
    """List all indexes in the database"""
    try:
        db = get_db()
        
        indexes = {}
        collections = ['events', 'venues', 'users', 'tickets', 'checkins', 'reviews']
        
        for collection_name in collections:
            collection = db[collection_name]
            collection_indexes = list(collection.list_indexes())
            indexes[collection_name] = []
            
            for index in collection_indexes:
                indexes[collection_name].append({
                    'name': index['name'],
                    'key': index.get('key', {}),
                    'unique': index.get('unique', False),
                    'sparse': index.get('sparse', False),
                    'background': index.get('background', False)
                })
        
        return jsonify({
            'indexes': indexes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/stats', methods=['GET'])
def database_stats():
    """Get database statistics"""
    try:
        db = get_db()
        
        # Get collection stats
        stats = {}
        collections = ['events', 'venues', 'users', 'tickets', 'checkins', 'reviews']
        
        for collection_name in collections:
            collection = db[collection_name]
            stats[collection_name] = {
                'count': collection.count_documents({}),
                'size': collection.estimated_document_count()
            }
        
        # Get database stats
        db_stats = db.command('dbStats')
        
        return jsonify({
            'collections': stats,
            'database': {
                'name': db_stats['db'],
                'collections': db_stats['collections'],
                'data_size': db_stats['dataSize'],
                'storage_size': db_stats['storageSize'],
                'indexes': db_stats['indexes'],
                'index_size': db_stats['indexSize']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/saved-queries', methods=['GET'])
def list_saved_queries():
    """List all saved queries for performance testing"""
    try:
        saved_queries = {
            'text_search': {
                'name': 'Text Search',
                'description': 'Search events by text content',
                'collection': 'events',
                'type': 'find'
            },
            'geo_nearby': {
                'name': 'Geospatial Nearby',
                'description': 'Find events near a location',
                'collection': 'events',
                'type': 'aggregation'
            },
            'venue_events': {
                'name': 'Venue Events',
                'description': 'Get events for a specific venue',
                'collection': 'events',
                'type': 'find'
            },
            'user_tickets': {
                'name': 'User Tickets',
                'description': 'Get tickets for a specific user',
                'collection': 'tickets',
                'type': 'find'
            }
        }
        
        return jsonify({
            'saved_queries': saved_queries
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
