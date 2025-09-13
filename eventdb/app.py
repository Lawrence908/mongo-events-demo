from flask import Flask, render_template
from pymongo import MongoClient
import os

from config import Config


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize MongoDB connection
    client = MongoClient(Config.MONGODB_URI)
    app.mongo = client[Config.DB_NAME]
    
    # Register blueprints
    from routes.events import bp as events_bp
    from routes.venues import bp as venues_bp
    from routes.users import bp as users_bp
    from routes.analytics import bp as analytics_bp
    from routes.admin import bp as admin_bp
    
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(venues_bp, url_prefix="/venues")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    
    @app.route("/")
    def home():
        """Home page with tabs for all demos"""
        return render_template("index.html")
    
    @app.route("/api/events/nearby")
    def api_events_nearby():
        """API: Get nearby events as GeoJSON"""
        from routes.events import get_nearby_events_geojson
        return get_nearby_events_geojson()
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
