"""
Real-time Event Updates using WebSockets
Demonstrates MongoDB Change Streams for live event notifications
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from pymongo import MongoClient
from bson import ObjectId

from .database import get_mongodb
from .models import Event

class RealtimeEventService:
    """Service for real-time event updates using WebSockets and MongoDB Change Streams"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.db = None
        self.change_stream = None
        self._setup_change_stream()
    
    def _setup_change_stream(self):
        """Set up MongoDB change stream for real-time updates"""
        try:
            self.db = get_mongodb()
            # Watch for changes in the events collection
            self.change_stream = self.db.events.watch()
            print("✅ MongoDB Change Stream initialized")
        except Exception as e:
            print(f"❌ Failed to initialize change stream: {e}")
    
    def start_listening(self):
        """Start listening to MongoDB changes and broadcast via WebSocket"""
        if not self.change_stream:
            return
        
        def process_change(change):
            """Process MongoDB change and broadcast to WebSocket clients"""
            try:
                change_type = change['operationType']
                document = change.get('fullDocument', {})
                document_id = change.get('documentKey', {}).get('_id')
                
                if change_type == 'insert':
                    self._broadcast_event_created(document)
                elif change_type == 'update':
                    self._broadcast_event_updated(document_id, change.get('updateDescription', {}))
                elif change_type == 'delete':
                    self._broadcast_event_deleted(document_id)
                    
            except Exception as e:
                print(f"Error processing change: {e}")
        
        # Process changes in a separate thread
        import threading
        
        def listen_to_changes():
            for change in self.change_stream:
                process_change(change)
        
        thread = threading.Thread(target=listen_to_changes, daemon=True)
        thread.start()
        print("🔄 Change stream listener started")
    
    def _broadcast_event_created(self, event_data: Dict[str, Any]):
        """Broadcast new event to all connected clients"""
        try:
            event = Event(**event_data)
            self.socketio.emit('event_created', {
                'event': event.model_dump(),
                'timestamp': datetime.utcnow().isoformat()
            }, namespace='/events')
            print(f"📢 Broadcasted event created: {event.title}")
        except Exception as e:
            print(f"Error broadcasting event created: {e}")
    
    def _broadcast_event_updated(self, event_id: ObjectId, update_description: Dict[str, Any]):
        """Broadcast event update to all connected clients"""
        try:
            # Get the updated event
            event_data = self.db.events.find_one({"_id": event_id})
            if event_data:
                event = Event(**event_data)
                self.socketio.emit('event_updated', {
                    'event_id': str(event_id),
                    'event': event.model_dump(),
                    'updated_fields': list(update_description.get('updatedFields', {}).keys()),
                    'timestamp': datetime.utcnow().isoformat()
                }, namespace='/events')
                print(f"📢 Broadcasted event updated: {event.title}")
        except Exception as e:
            print(f"Error broadcasting event updated: {e}")
    
    def _broadcast_event_deleted(self, event_id: ObjectId):
        """Broadcast event deletion to all connected clients"""
        try:
            self.socketio.emit('event_deleted', {
                'event_id': str(event_id),
                'timestamp': datetime.utcnow().isoformat()
            }, namespace='/events')
            print(f"📢 Broadcasted event deleted: {event_id}")
        except Exception as e:
            print(f"Error broadcasting event deleted: {e}")
    
    def broadcast_analytics_update(self, analytics_data: Dict[str, Any]):
        """Broadcast analytics updates to subscribed clients"""
        try:
            self.socketio.emit('analytics_updated', {
                'analytics': analytics_data,
                'timestamp': datetime.utcnow().isoformat()
            }, namespace='/analytics')
            print("📊 Broadcasted analytics update")
        except Exception as e:
            print(f"Error broadcasting analytics: {e}")

# WebSocket event handlers
def register_socket_handlers(socketio: SocketIO):
    """Register WebSocket event handlers"""
    
    @socketio.on('connect', namespace='/events')
    def handle_events_connect():
        """Handle client connection to events namespace"""
        print(f"Client connected to events namespace: {request.sid}")
        emit('connected', {'message': 'Connected to real-time events'})
    
    @socketio.on('disconnect', namespace='/events')
    def handle_events_disconnect():
        """Handle client disconnection from events namespace"""
        print(f"Client disconnected from events namespace: {request.sid}")
    
    @socketio.on('join_location', namespace='/events')
    def handle_join_location(data):
        """Join a location-based room for localized updates"""
        try:
            longitude = data.get('longitude')
            latitude = data.get('latitude')
            radius = data.get('radius', 50)
            
            if longitude and latitude:
                room_name = f"location_{longitude}_{latitude}_{radius}"
                join_room(room_name)
                emit('joined_location', {
                    'room': room_name,
                    'longitude': longitude,
                    'latitude': latitude,
                    'radius': radius
                })
                print(f"Client joined location room: {room_name}")
        except Exception as e:
            emit('error', {'message': f'Failed to join location: {str(e)}'})
    
    @socketio.on('leave_location', namespace='/events')
    def handle_leave_location(data):
        """Leave a location-based room"""
        try:
            longitude = data.get('longitude')
            latitude = data.get('latitude')
            radius = data.get('radius', 50)
            
            if longitude and latitude:
                room_name = f"location_{longitude}_{latitude}_{radius}"
                leave_room(room_name)
                emit('left_location', {'room': room_name})
                print(f"Client left location room: {room_name}")
        except Exception as e:
            emit('error', {'message': f'Failed to leave location: {str(e)}'})
    
    @socketio.on('join_category', namespace='/events')
    def handle_join_category(data):
        """Join a category-based room for category-specific updates"""
        try:
            category = data.get('category')
            if category:
                room_name = f"category_{category}"
                join_room(room_name)
                emit('joined_category', {
                    'room': room_name,
                    'category': category
                })
                print(f"Client joined category room: {room_name}")
        except Exception as e:
            emit('error', {'message': f'Failed to join category: {str(e)}'})
    
    @socketio.on('connect', namespace='/analytics')
    def handle_analytics_connect():
        """Handle client connection to analytics namespace"""
        print(f"Client connected to analytics namespace: {request.sid}")
        emit('connected', {'message': 'Connected to real-time analytics'})
    
    @socketio.on('disconnect', namespace='/analytics')
    def handle_analytics_disconnect():
        """Handle client disconnection from analytics namespace"""
        print(f"Client disconnected from analytics namespace: {request.sid}")

# Global realtime service instance
_realtime_service = None

def get_realtime_service(socketio: SocketIO) -> RealtimeEventService:
    """Get or create realtime service instance"""
    global _realtime_service
    if _realtime_service is None:
        _realtime_service = RealtimeEventService(socketio)
    return _realtime_service

def init_realtime(socketio: SocketIO):
    """Initialize real-time features"""
    register_socket_handlers(socketio)
    realtime_service = get_realtime_service(socketio)
    realtime_service.start_listening()
    return realtime_service
