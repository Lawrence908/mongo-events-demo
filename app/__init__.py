import os

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_socketio import SocketIO
from pydantic import ValidationError

from .database import mongodb
from .models import EventCreate, EventsNearbyQuery, EventUpdate
from .services import get_event_service
from .realtime import init_realtime

load_dotenv()


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["MONGODB_URI"] = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    app.config["MONGODB_DB_NAME"] = os.getenv("MONGODB_DB_NAME", "events_demo")

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
        return render_template("index.html")
    
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

        events = get_event_service().get_events(
            skip=skip, limit=per_page, category=category, search=search
        )
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
                    "start_date": request.form["start_date"],
                    "end_date": request.form.get("end_date") or None,
                    "organizer": request.form.get("organizer"),
                    "max_attendees": int(request.form["max_attendees"])
                    if request.form.get("max_attendees")
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
        """API: Get events"""
        try:
            page = int(request.args.get("page", 1))
            per_page = min(int(request.args.get("per_page", 50)), 100)
            skip = (page - 1) * per_page

            category = request.args.get("category")
            search = request.args.get("search")

            result = get_event_service().get_events(
                skip=skip, limit=per_page, category=category, search=search
            )
            events = result["events"] if isinstance(result, dict) else result

            return jsonify(
                {
                    "events": [event.model_dump() for event in events],
                    "page": page,
                    "per_page": per_page,
                    "pagination": result if isinstance(result, dict) else None
                }
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events/nearby", methods=["GET"])
    def api_events_nearby():
        """API: Get nearby events as GeoJSON"""
        try:
            query_params = {
                "longitude": float(request.args.get("lng", 0)),
                "latitude": float(request.args.get("lat", 0)),
                "radius_km": float(request.args.get("radius", 10)),
                "limit": min(int(request.args.get("limit", 50)), 100),
            }

            query = EventsNearbyQuery(**query_params)
            geojson = get_event_service().get_events_nearby(query)

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
        """API: Get events this weekend near a location"""
        try:
            longitude = float(request.args.get("lng", -74.0060))  # Default to NYC
            latitude = float(request.args.get("lat", 40.7128))
            radius_km = float(request.args.get("radius", 50))
            
            weekend_events = get_event_service().get_events_this_weekend(
                longitude, latitude, radius_km
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
            
            start_date = datetime.fromisoformat(request.args.get("start_date"))
            end_date = datetime.fromisoformat(request.args.get("end_date"))
            category = request.args.get("category")
            longitude = request.args.get("lng", type=float)
            latitude = request.args.get("lat", type=float)
            radius_km = request.args.get("radius", type=float)
            
            events = get_event_service().get_events_by_date_range(
                start_date, end_date, category, longitude, latitude, radius_km
            )
            
            return jsonify({
                "events": [event.model_dump() for event in events],
                "count": len(events),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            })
            
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
