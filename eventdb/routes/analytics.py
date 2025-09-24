from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta, timezone

from ..config import Config

bp = Blueprint('analytics', __name__)


def get_db():
    """Get database connection"""
    client = MongoClient(Config.MONGODB_URI)
    return client[Config.DB_NAME]


@bp.route('/attendance-by-day/<event_id>', methods=['GET'])
def attendance_by_day(event_id):
    """Get attendance data for a specific event by day"""
    try:
        db = get_db()
        
        # Aggregation pipeline for daily attendance
        pipeline = [
            {'$match': {'eventId': ObjectId(event_id)}},
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$at'},
                        'month': {'$month': '$at'},
                        'day': {'$dayOfMonth': '$at'}
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {
                    '_id.year': 1,
                    '_id.month': 1,
                    '_id.day': 1
                }
            }
        ]
        
        results = list(db.checkins.aggregate(pipeline))
        
        # Format results
        attendance_data = []
        for result in results:
            date = datetime(
                result['_id']['year'],
                result['_id']['month'],
                result['_id']['day']
            ).strftime('%Y-%m-%d')
            attendance_data.append({
                'date': date,
                'attendance': result['count']
            })
        
        return jsonify({
            'event_id': event_id,
            'attendance_by_day': attendance_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/top-venues', methods=['GET'])
def top_venues():
    """Get top venues by event count"""
    try:
        limit = int(request.args.get('limit', 5))
        db = get_db()
        
        # Aggregation pipeline for top venues
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
                '$group': {
                    '_id': '$venueId',
                    'venue_name': {'$first': '$venue.name'},
                    'venue_address': {'$first': '$venue.address'},
                    'event_count': {'$sum': 1}
                }
            },
            {'$sort': {'event_count': -1}},
            {'$limit': limit}
        ]
        
        results = list(db.events.aggregate(pipeline))
        
        # Format results
        top_venues = []
        for result in results:
            top_venues.append({
                'venue_id': str(result['_id']),
                'venue_name': result['venue_name'],
                'venue_address': result['venue_address'],
                'event_count': result['event_count']
            })
        
        return jsonify({
            'top_venues': top_venues,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/sales-by-month', methods=['GET'])
def sales_by_month():
    """Get ticket sales by month"""
    try:
        db = get_db()
        
        # Aggregation pipeline for monthly sales
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$purchasedAt'},
                        'month': {'$month': '$purchasedAt'}
                    },
                    'total_sales': {'$sum': '$pricePaid'},
                    'ticket_count': {'$sum': 1}
                }
            },
            {
                '$sort': {
                    '_id.year': 1,
                    '_id.month': 1
                }
            }
        ]
        
        results = list(db.tickets.aggregate(pipeline))
        
        # Format results
        sales_data = []
        for result in results:
            month = datetime(
                result['_id']['year'],
                result['_id']['month'],
                1
            ).strftime('%Y-%m')
            sales_data.append({
                'month': month,
                'total_sales': result['total_sales'],
                'ticket_count': result['ticket_count']
            })
        
        return jsonify({
            'sales_by_month': sales_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/event-stats', methods=['GET'])
def event_stats():
    """Get general event statistics"""
    try:
        db = get_db()
        
        # Get basic counts
        total_events = db.events.count_documents({})
        total_venues = db.venues.count_documents({})
        total_users = db.users.count_documents({})
        total_tickets = db.tickets.count_documents({})
        total_checkins = db.checkins.count_documents({})
        
        # Get events by status (active tickets)
        active_tickets = db.tickets.count_documents({'status': 'active'})
        cancelled_tickets = db.tickets.count_documents({'status': 'cancelled'})
        used_tickets = db.tickets.count_documents({'status': 'used'})
        
        # Get upcoming events
        upcoming_events = db.events.count_documents({
            'datetime': {'$gt': datetime.now(timezone.utc)}
        })
        
        # Get total revenue
        revenue_result = db.tickets.aggregate([
            {'$group': {'_id': None, 'total_revenue': {'$sum': '$pricePaid'}}}
        ])
        total_revenue = list(revenue_result)[0]['total_revenue'] if revenue_result else 0
        
        return jsonify({
            'total_events': total_events,
            'total_venues': total_venues,
            'total_users': total_users,
            'total_tickets': total_tickets,
            'total_checkins': total_checkins,
            'ticket_status': {
                'active': active_tickets,
                'cancelled': cancelled_tickets,
                'used': used_tickets
            },
            'upcoming_events': upcoming_events,
            'total_revenue': total_revenue
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
