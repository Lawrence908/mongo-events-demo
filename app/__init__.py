import os

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_socketio import SocketIO
from pydantic import ValidationError

from .database import mongodb
from .models import EventCreate, EventsNearbyQuery, EventUpdate, CheckinCreate, CheckinUpdate
from .services import get_event_service, get_checkin_service
from .realtime import init_realtime
from .config import Config

load_dotenv()


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["MONGODB_URI"] = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    app.config["MONGODB_DB_NAME"] = os.getenv("MONGODB_DB_NAME", "events_demo")
    app.config["GOOGLE_MAPS_API_KEY"] = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # Initialize SocketIO for real-time features
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Initialize real-time features
    init_realtime(socketio)

    # Initialize database connection (lazy)
    # Connection will be established when first needed

    # Routes
    @app.route("/")
    def index():
        """Home page with event map"""
        return render_template("index.html", max_events_limit=Config.MAX_EVENTS_LIMIT)
    
    @app.route("/realtime")
    def realtime_demo():
        """Real-time events demo page"""
        return render_template("realtime_demo.html")

    @app.route("/events")
    def events_list():
        """Events list page"""
        page = int(request.args.get("page", 1))
        per_page = 10
        skip = (page - 1) * per_page

        category = request.args.get("category")
        search = request.args.get("search")

        result = get_event_service().get_events(
            skip=skip, limit=per_page, category=category, search=search
        )
        events = result["events"] if isinstance(result, dict) else result
        categories = get_event_service().get_categories()

        return render_template(
            "events_list.html",
            events=events,
            categories=categories,
            current_category=category,
            current_search=search,
            page=page,
        )

    @app.route("/events/<event_id>")
    def event_detail(event_id):
        """Event detail page"""
        event = get_event_service().get_event(event_id)
        if not event:
            flash("Event not found", "error")
            return redirect(url_for("events_list"))

        return render_template("event_detail.html", event=event)

    @app.route("/events/new", methods=["GET", "POST"])
    def create_event():
        """Create new event"""
        if request.method == "POST":
            try:
                # Extract form data
                form_data = {
                    "title": request.form["title"],
                    "description": request.form.get("description"),
                    "category": request.form["category"],
                    "location": {
                        "type": "Point",
                        "coordinates": [
                            float(request.form["longitude"]),
                            float(request.form["latitude"]),
                        ],
                    },
                    "startDate": request.form["startDate"],
                    "endDate": request.form.get("endDate") or None,
                    "organizer": request.form.get("organizer"),
                    "maxAttendees": int(request.form["maxAttendees"])
                    if request.form.get("maxAttendees")
                    else None,
                    "tags": [
                        tag.strip()
                        for tag in request.form.get("tags", "").split(",")
                        if tag.strip()
                    ],
                }

                event_data = EventCreate(**form_data)
                event = get_event_service().create_event(event_data)

                flash("Event created successfully!", "success")
                return redirect(url_for("event_detail", event_id=str(event.id)))

            except ValidationError as e:
                flash(f"Validation error: {e}", "error")
            except Exception as e:
                flash(f"Error creating event: {e}", "error")

        return render_template("create_event.html")

    # API Routes
    @app.route("/api/events", methods=["GET"])
    def api_get_events():
        """API: Get events with cursor-based pagination and text search
        
        Supports:
        - /api/events?q=search_term (text search with relevance scoring)
        - /api/events?search=search_term (alternative parameter name)
        - /api/events?category=music (category filtering)
        - /api/events?cursor_id=... (cursor-based pagination)
        """
        try:
            # Support both cursor-based and offset-based pagination
            cursor_id = request.args.get("cursor_id")
            page = int(request.args.get("page", 1))
            per_page = min(int(request.args.get("per_page", 50)), 100)
            skip = (page - 1) * per_page

            category = request.args.get("category")
            # Support both 'q' and 'search' parameters for text search
            search = request.args.get("q") or request.args.get("search")

            result = get_event_service().get_events(
                skip=skip, 
                limit=per_page, 
                category=category, 
                search=search,
                cursor_id=cursor_id
            )
            events = result["events"] if isinstance(result, dict) else result

            # Convert events to dictionaries for JSON serialization
            events_data = []
            for event in events:
                try:
                    event_dict = event.model_dump()
                    events_data.append(event_dict)
                except Exception as e:
                    print(f"Error serializing event {event.title}: {e}")
                    # Fallback to manual conversion
                    event_dict = {
                        "id": str(event.id) if event.id else None,
                        "title": event.title,
                        "description": event.description,
                        "category": event.category,
                        "location": event.location.model_dump() if event.location else None,
                        "startDate": event.startDate.isoformat() if event.startDate else None,
                        "endDate": event.endDate.isoformat() if event.endDate else None,
                        "organizer": event.organizer,
                        "maxAttendees": event.maxAttendees,
                        "tags": event.tags,
                        "createdAt": event.createdAt.isoformat() if event.createdAt else None,
                        "updatedAt": event.updatedAt.isoformat() if event.updatedAt else None,
                        "score": getattr(event, 'score', None)
                    }
                    events_data.append(event_dict)
            
            # Ensure pagination data is also JSON serializable
            pagination_data = None
            if isinstance(result, dict):
                pagination_data = {
                    "next_cursor": result.get("next_cursor"),
                    "has_more": result.get("has_more"),
                    "pagination_type": result.get("pagination_type"),
                    "offset": result.get("offset")
                }
            
            response_data = {
                "events": events_data,
                "page": page,
                "per_page": per_page,
                "pagination": pagination_data
            }
            
            # Include search query in response for debugging
            if search:
                response_data["search_query"] = search
                response_data["search_type"] = "text_search_with_relevance_scoring"

            return jsonify(response_data)

        except Exception as e:
            import traceback
            print(f"Error in API endpoint: {e}")
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events/nearby", methods=["GET"])
    def api_events_nearby():
        """API: Get nearby events as GeoJSON with optional category filtering"""
        try:
            query_params = {
                "longitude": float(request.args.get("lng", 0)),
                "latitude": float(request.args.get("lat", 0)),
                "radius_km": float(request.args.get("radius", 10)),
                "limit": min(int(request.args.get("limit", 50)), Config.MAX_EVENTS_LIMIT),
            }
            
            # Optional category filter
            category = request.args.get("category")

            query = EventsNearbyQuery(**query_params)
            geojson = get_event_service().get_events_nearby(query, category=category)

            return jsonify(geojson)

        except ValidationError as e:
            return (
                jsonify({"error": "Invalid query parameters", "details": e.errors()}),
                400,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events", methods=["POST"])
    def api_create_event():
        """API: Create event"""
        try:
            data = request.get_json()
            event_data = EventCreate(**data)
            event = get_event_service().create_event(event_data)

            return jsonify(event.model_dump()), 201

        except ValidationError as e:
            return jsonify({"error": "Validation failed", "details": e.errors()}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events/<event_id>", methods=["GET"])
    def api_get_event(event_id):
        """API: Get single event"""
        event = get_event_service().get_event(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

        return jsonify(event.dict())

    @app.route("/api/events/<event_id>", methods=["PUT"])
    def api_update_event(event_id):
        """API: Update event"""
        try:
            data = request.get_json()
            event_data = EventUpdate(**data)
            event = get_event_service().update_event(event_id, event_data)

            if not event:
                return jsonify({"error": "Event not found"}), 404

            return jsonify(event.model_dump())

        except ValidationError as e:
            return jsonify({"error": "Validation failed", "details": e.errors()}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events/<event_id>", methods=["DELETE"])
    def api_delete_event(event_id):
        """API: Delete event"""
        success = get_event_service().delete_event(event_id)
        if not success:
            return jsonify({"error": "Event not found"}), 404

        return "", 204

    @app.route("/api/categories", methods=["GET"])
    def api_get_categories():
        """API: Get event categories"""
        categories = get_event_service().get_categories()
        return jsonify({"categories": categories})

    @app.route("/api/events/weekend", methods=["GET"])
    def api_events_weekend():
        """API: Get events this weekend near a location with optional category filtering"""
        try:
            longitude = float(request.args.get("lng", -74.0060))  # Default to NYC
            latitude = float(request.args.get("lat", 40.7128))
            radius_km = float(request.args.get("radius", 50))
            category = request.args.get("category")  # Optional category filter
            
            weekend_events = get_event_service().get_events_this_weekend(
                longitude, latitude, radius_km, category=category
            )
            return jsonify(weekend_events)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/analytics", methods=["GET"])
    def api_analytics():
        """API: Get event analytics"""
        try:
            analytics = get_event_service().get_analytics()
            return jsonify(analytics)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events/date-range", methods=["GET"])
    def api_events_date_range():
        """API: Get events within a date range"""
        try:
            from datetime import datetime
            
            startDate = datetime.fromisoformat(request.args.get("startDate"))
            endDate = datetime.fromisoformat(request.args.get("endDate"))
            category = request.args.get("category")
            longitude = request.args.get("lng", type=float)
            latitude = request.args.get("lat", type=float)
            radius_km = request.args.get("radius", type=float)
            
            events = get_event_service().get_events_by_date_range(
                startDate, endDate, category, longitude, latitude, radius_km
            )
            
            return jsonify({
                "events": [event.model_dump() for event in events],
                "count": len(events),
                "date_range": {
                    "start": startDate.isoformat(),
                    "end": endDate.isoformat()
                }
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Enhanced Check-ins API Endpoints
    @app.route("/api/checkins", methods=["POST"])
    def api_create_checkin():
        """API: Create check-in with duplicate prevention"""
        try:
            data = request.get_json()
            checkin_data = CheckinCreate(**data)
            checkin = get_checkin_service().create_checkin(checkin_data)
            
            return jsonify(checkin.model_dump()), 201
            
        except ValidationError as e:
            return jsonify({"error": "Validation failed", "details": e.errors()}), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 409  # Conflict for duplicate check-in
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/<checkin_id>", methods=["GET"])
    def api_get_checkin(checkin_id):
        """API: Get single check-in"""
        checkin = get_checkin_service().get_checkin(checkin_id)
        if not checkin:
            return jsonify({"error": "Check-in not found"}), 404
        
        return jsonify(checkin.model_dump())

    @app.route("/api/checkins/<checkin_id>", methods=["PUT"])
    def api_update_checkin(checkin_id):
        """API: Update check-in"""
        try:
            data = request.get_json()
            checkin_data = CheckinUpdate(**data)
            checkin = get_checkin_service().update_checkin(checkin_id, checkin_data)
            
            if not checkin:
                return jsonify({"error": "Check-in not found"}), 404
            
            return jsonify(checkin.model_dump())
            
        except ValidationError as e:
            return jsonify({"error": "Validation failed", "details": e.errors()}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/<checkin_id>", methods=["DELETE"])
    def api_delete_checkin(checkin_id):
        """API: Delete check-in"""
        success = get_checkin_service().delete_checkin(checkin_id)
        if not success:
            return jsonify({"error": "Check-in not found"}), 404
        
        return "", 204

    @app.route("/api/checkins/event/<event_id>", methods=["GET"])
    def api_get_checkins_by_event(event_id):
        """API: Get check-ins for a specific event"""
        try:
            skip = request.args.get("skip", 0, type=int)
            limit = request.args.get("limit", 50, type=int)
            
            result = get_checkin_service().get_checkins_by_event(event_id, skip, limit)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/user/<user_id>", methods=["GET"])
    def api_get_checkins_by_user(user_id):
        """API: Get check-ins for a specific user"""
        try:
            skip = request.args.get("skip", 0, type=int)
            limit = request.args.get("limit", 50, type=int)
            
            result = get_checkin_service().get_checkins_by_user(user_id, skip, limit)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/venue/<venue_id>", methods=["GET"])
    def api_get_checkins_by_venue(venue_id):
        """API: Get check-ins for a specific venue (analytics)"""
        try:
            skip = request.args.get("skip", 0, type=int)
            limit = request.args.get("limit", 50, type=int)
            
            result = get_checkin_service().get_checkins_by_venue(venue_id, skip, limit)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/analytics/event/<event_id>", methods=["GET"])
    def api_get_event_attendance_stats(event_id):
        """API: Get attendance statistics for a specific event"""
        try:
            stats = get_checkin_service().get_attendance_stats_by_event(event_id)
            return jsonify(stats)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/analytics/venue/<venue_id>", methods=["GET"])
    def api_get_venue_attendance_stats(venue_id):
        """API: Get attendance statistics for a specific venue"""
        try:
            from datetime import datetime
            
            startDate = request.args.get("startDate")
            endDate = request.args.get("endDate")
            
            startDate = datetime.fromisoformat(startDate) if startDate else None
            endDate = datetime.fromisoformat(endDate) if endDate else None
            
            stats = get_checkin_service().get_venue_attendance_stats(venue_id, startDate, endDate)
            return jsonify(stats)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/analytics/repeat-attendees", methods=["GET"])
    def api_get_repeat_attendees():
        """API: Get repeat attendees (users who attended multiple events)"""
        try:
            min_events = request.args.get("min_events", 2, type=int)
            attendees = get_checkin_service().get_repeat_attendees(min_events)
            return jsonify({"repeat_attendees": attendees, "count": len(attendees)})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/analytics/time-patterns", methods=["GET"])
    def api_get_checkin_time_patterns():
        """API: Get check-in time patterns (peak hours, days of week)"""
        try:
            venue_id = request.args.get("venue_id")
            patterns = get_checkin_service().get_checkin_time_patterns(venue_id)
            return jsonify(patterns)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/checkins/analytics/user/<user_id>/history", methods=["GET"])
    def api_get_user_attendance_history(user_id):
        """API: Get detailed attendance history for a user"""
        try:
            limit = request.args.get("limit", 50, type=int)
            history = get_checkin_service().get_user_attendance_history(user_id, limit)
            return jsonify(history)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    return app, socketio


# Create app instance
app, socketio = create_app()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"

    socketio.run(app, host=host, port=port, debug=debug)
