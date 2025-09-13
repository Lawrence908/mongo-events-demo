#!/usr/bin/env python3
"""
MongoDB Events Demo - Application Entry Point
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config

if __name__ == "__main__":
    app = create_app()
    
    print("MongoDB Events Demo")
    print("=" * 50)
    print(f"Database Type: {Config.DB_TYPE}")
    print(f"Database URI: {Config.MONGODB_URI}")
    print(f"Database Name: {Config.DB_NAME}")
    print(f"Host: {Config.HOST}")
    print(f"Port: {Config.PORT}")
    print(f"Debug: {Config.DEBUG}")
    print("=" * 50)
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
