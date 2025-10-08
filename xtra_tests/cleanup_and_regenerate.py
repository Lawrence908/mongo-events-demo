#!/usr/bin/env python3
"""
Cleanup and Regenerate Script for EventSphere
This script helps clean up the old tickets collection and regenerate data properly
"""

import sys
import os

# Add eventdb directory to path for config import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'eventdb'))

try:
    from config import Config
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("Error: MongoDB integration not available. Install pymongo and ensure config.py is accessible.")

def cleanup_database():
    """Clean up the database and remove old tickets collection"""
    if not MONGODB_AVAILABLE:
        print("❌ Cannot connect to MongoDB")
        return False
    
    try:
        print("🧹 Cleaning up database...")
        client = MongoClient(Config.MONGODB_URI)
        db = client[Config.DB_NAME]
        
        # List current collections
        collections = db.list_collection_names()
        print(f"Current collections: {collections}")
        
        # Clear tickets collection (user purchases)
        if "tickets" in collections:
            print("Clearing tickets collection (user purchases)...")
            db.tickets.drop()
            print("✓ Tickets collection cleared")
        else:
            print("✓ No tickets collection found")
        
        # Clear all other collections
        for collection_name in ["events", "venues", "users", "checkins", "reviews"]:
            if collection_name in collections:
                print(f"Clearing {collection_name} collection...")
                db[collection_name].drop()
                print(f"✓ {collection_name} collection cleared")
        
        client.close()
        print("✅ Database cleanup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False

def main():
    """Main function"""
    print("EventSphere - Database Cleanup and Regeneration")
    print("=" * 60)
    
    # Step 1: Cleanup
    if cleanup_database():
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Run the updated data generator:")
        print("   python generate_test_data.py --seed-db --clear-db")
        print("\n2. Or generate JSON files first:")
        print("   python generate_test_data.py --json-only")
        print("\n3. The new generator will:")
        print("   - Create events with embedded EventTickets (ticket types available)")
        print("   - Create separate tickets collection (user purchases)")
        print("   - Include proper error handling")
        print("   - Show detailed progress and statistics")
        print("\n4. Verify in Atlas that you now have:")
        print("   - events (with embedded EventTickets for ticket types)")
        print("   - tickets (user purchases with eventId/userId references)")
        print("   - venues")
        print("   - users") 
        print("   - checkins")
        print("   - reviews")
    else:
        print("❌ Cleanup failed. Please check your MongoDB connection.")

if __name__ == "__main__":
    main()
