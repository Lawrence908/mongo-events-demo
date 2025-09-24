#!/usr/bin/env python3
"""
Demonstrate MongoDB transactions for ticket purchasing
"""
import os
import sys
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


def buy_ticket(event_id, user_id, price_paid):
    """
    Purchase a ticket using MongoDB transactions
    """
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.DB_NAME]
    
    # Convert string IDs to ObjectId
    event_id = ObjectId(event_id)
    user_id = ObjectId(user_id)
    
    # Start a session for the transaction
    with client.start_session() as session:
        try:
            with session.start_transaction():
                # Check if event exists and has available seats
                event = db.events.find_one({"_id": event_id}, session=session)
                if not event:
                    raise ValueError("Event not found")
                
                if event["seatsAvailable"] <= 0:
                    raise ValueError("No seats available")
                
                # Decrement available seats
                result = db.events.update_one(
                    {"_id": event_id, "seatsAvailable": {"$gt": 0}},
                    {"$inc": {"seatsAvailable": -1}},
                    session=session
                )
                
                if result.modified_count == 0:
                    raise ValueError("Failed to reserve seat - may have been sold out")
                
                # Create ticket
                ticket = {
                    "eventId": event_id,
                    "userId": user_id,
                    "pricePaid": price_paid,
                    "status": "active",
                    "purchasedAt": datetime.now(timezone.utc)
                }
                
                ticket_result = db.tickets.insert_one(ticket, session=session)
                
                # Get updated event info
                updated_event = db.events.find_one({"_id": event_id}, session=session)
                
                return {
                    "success": True,
                    "ticket_id": str(ticket_result.inserted_id),
                    "event_title": event["title"],
                    "seats_remaining": updated_event["seatsAvailable"],
                    "price_paid": price_paid
                }
                
        except Exception as e:
            print(f"Transaction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def demo_transaction():
    """Demonstrate the transaction process"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.DB_NAME]
    
    print("MongoDB Transactions Demo - Ticket Purchase")
    print("=" * 50)
    
    # Get a sample event and user
    event = db.events.find_one({"seatsAvailable": {"$gt": 0}})
    user = db.users.find_one()
    
    if not event or not user:
        print("❌ No events with available seats or users found")
        return
    
    print(f"Event: {event['title']}")
    print(f"Available seats: {event['seatsAvailable']}")
    print(f"Price: ${event.get('price', 0):.2f}")
    print(f"User: {user['name']} ({user['email']})")
    print()
    
    # Attempt to buy a ticket
    result = buy_ticket(
        str(event["_id"]),
        str(user["_id"]),
        event.get("price", 0)
    )
    
    if result["success"]:
        print("✅ Ticket purchased successfully!")
        print(f"   Ticket ID: {result['ticket_id']}")
        print(f"   Seats remaining: {result['seats_remaining']}")
        print(f"   Price paid: ${result['price_paid']:.2f}")
    else:
        print(f"❌ Purchase failed: {result['error']}")
    
    print()
    
    # Show updated event info
    updated_event = db.events.find_one({"_id": event["_id"]})
    print(f"Updated seats available: {updated_event['seatsAvailable']}")


def stress_test_transactions():
    """Test concurrent ticket purchases"""
    import threading
    import time
    
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.DB_NAME]
    
    # Get an event with limited seats
    event = db.events.find_one({"seatsAvailable": {"$gt": 0}})
    if not event:
        print("❌ No events with available seats found")
        return
    
    print(f"\nStress Test - Attempting to sell {event['seatsAvailable']} tickets concurrently")
    print("=" * 60)
    
    results = []
    
    def purchase_ticket(thread_id):
        user = db.users.find_one()
        if user:
            result = buy_ticket(
                str(event["_id"]),
                str(user["_id"]),
                event.get("price", 0)
            )
            result["thread_id"] = thread_id
            results.append(result)
    
    # Create threads for concurrent purchases
    threads = []
    for i in range(min(event["seatsAvailable"] + 5, 20)):  # Try to oversell
        thread = threading.Thread(target=purchase_ticket, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Analyze results
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"Total attempts: {len(results)}")
    print(f"Successful purchases: {len(successful)}")
    print(f"Failed purchases: {len(failed)}")
    
    # Show final event state
    final_event = db.events.find_one({"_id": event["_id"]})
    print(f"Final seats available: {final_event['seatsAvailable']}")
    
    if failed:
        print("\nSample failure reasons:")
        for i, fail in enumerate(failed[:3]):
            print(f"  {i+1}. {fail['error']}")


if __name__ == "__main__":
    print(f"Using database: {Config.DB_NAME}")
    print(f"Connection: {Config.MONGODB_URI}")
    print()
    
    demo_transaction()
    
    # Uncomment to run stress test
    # stress_test_transactions()
