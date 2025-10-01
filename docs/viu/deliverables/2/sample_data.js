// Insert realistic sample data demonstrating relationships

// Users
const userAliceId = ObjectId();
const userBobId = ObjectId();
db.users.insertMany([
  {
    _id: userAliceId,
    email: "alice@example.com",
    schemaVersion: "1.0",
    profile: { first_name: "Alice", last_name: "Nguyen", preferences: { categories: ["Technology", "Music"], radius_km: 25 } },
    created_at: new Date(),
    last_login: new Date()
  },
  {
    _id: userBobId,
    email: "bob@example.com",
    schemaVersion: "1.0",
    profile: { first_name: "Bob", last_name: "Martinez", preferences: { categories: ["Sports"], radius_km: 10 } },
    created_at: new Date(),
    last_login: new Date()
  }
]);

// Venues
const venue1Id = ObjectId();
const venue2Id = ObjectId();
db.venues.insertMany([
  {
    _id: venue1Id,
    name: "Grand Conference Center - San Jose",
    venue_type: "conference_center",
    schemaVersion: "1.0",
    type: "Conference Center",
    description: "A conference center located in San Jose.",
    address: { street: "123 Main St", city: "San Jose", state: "CA", zip_code: "95112", country: "USA" },
    location: { type: "Point", coordinates: [-121.8863, 37.3382] },
    capacity: 800,
    amenities: ["WiFi", "Parking", "A/V"],
    contact: { phone: "(408) 555-1234", email: "info@grandcc.com", website: "https://grandcc.com" },
    pricing: { hourly_rate: 200, daily_rate: 1500, currency: "USD" },
    availability: { monday: { open: "09:00", close: "22:00" } },
    conference_center_details: {
      breakout_rooms: 8,
      a_v_equipment: ["Projectors", "Microphones", "Video Conferencing"],
      catering_available: true
    },
    rating: 4.5,
    review_count: 12,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: venue2Id,
    name: "City Park - Austin",
    venue_type: "park",
    schemaVersion: "1.0",
    type: "Park",
    description: "Outdoor venue in Austin.",
    address: { street: "200 Park Ave", city: "Austin", state: "TX", zip_code: "73301", country: "USA" },
    location: { type: "Point", coordinates: [-97.7431, 30.2672] },
    capacity: 1500,
    amenities: ["Parking", "Outdoor Space"],
    contact: { phone: "(512) 555-2000", email: "contact@cityparkaustin.org", website: "https://cityparkaustin.org" },
    pricing: { hourly_rate: 50, daily_rate: 300, currency: "USD" },
    park_details: {
      outdoor_space: true,
      parking_spaces: 200,
      restroom_facilities: true
    },
    rating: 4.1,
    review_count: 5,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// Events
const eventTechId = ObjectId();
const eventMusicId = ObjectId();
db.events.insertMany([
  {
    _id: eventTechId,
    title: "AI Workshop 2025",
    description: "Hands-on machine learning bootcamp.",
    category: "Technology",
    event_type: "in_person",
    schemaVersion: "1.0",
    location: { type: "Point", coordinates: [-121.8863, 37.3382] },
    venueId: venue1Id,
    venue_reference: {
      name: "Grand Conference Center - San Jose",
      city: "San Jose",
      capacity: 800,
      venue_type: "conference_center"
    },
    start_date: new Date(Date.now() + 7*24*60*60*1000),
    end_date: new Date(Date.now() + 7*24*60*60*1000 + 3*60*60*1000),
    organizer: "TechCorp Events",
    max_attendees: 300,
    current_attendees: 25,
    price: 99,
    currency: "USD",
    is_free: false,
    status: "published",
    tickets: [
      { tier: "Early Bird", price: 79.2, available: 50, sold: 50 },
      { tier: "General Admission", price: 99, available: 200, sold: 0 },
      { tier: "VIP", price: 148.5, available: 20, sold: 0 }
    ],
    tags: ["learning", "technical", "workshop"],
    metadata: {
      age_restriction: "18+",
      dress_code: "Business Casual",
      accessibility_features: ["Wheelchair Accessible", "Sign Language Interpreter Available"]
    },
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: eventMusicId,
    title: "Jazz Night Downtown",
    description: "Live jazz with local artists.",
    category: "Music",
    event_type: "hybrid",
    schemaVersion: "1.0",
    location: { type: "Point", coordinates: [-97.7431, 30.2672] },
    venueId: venue2Id,
    venue_reference: {
      name: "City Park - Austin",
      city: "Austin",
      capacity: 1500,
      venue_type: "park"
    },
    start_date: new Date(Date.now() + 14*24*60*60*1000),
    end_date: new Date(Date.now() + 14*24*60*60*1000 + 4*60*60*1000),
    organizer: "City Arts",
    max_attendees: 500,
    current_attendees: 120,
    price: 25,
    currency: "USD",
    is_free: false,
    status: "published",
    tickets: [ { tier: "General Admission", price: 25, available: 350, sold: 150 } ],
    tags: ["music", "live", "entertainment"],
    hybrid_details: {
      virtual_capacity: 200,
      in_person_capacity: 300,
      virtual_meeting_url: "https://zoom.us/j/123456789"
    },
    metadata: {
      age_restriction: "All Ages",
      accessibility_features: ["Live Captioning", "Audio Description"]
    },
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// Reviews (event and venue)
db.reviews.insertMany([
  { user_id: userAliceId, event_id: eventTechId, rating: 5, comment: "Fantastic content!", schemaVersion: "1.0", created_at: new Date(), updated_at: new Date() },
  { user_id: userBobId, venue_id: venue2Id, rating: 4, comment: "Great outdoor vibe", schemaVersion: "1.0", created_at: new Date(), updated_at: new Date() }
]);

// Check-ins (bridge demonstrates many:many)
db.checkins.insertMany([
  {
    event_id: eventTechId,
    user_id: userAliceId,
    venue_id: venue1Id,
    check_in_time: new Date(Date.now() + 7*24*60*60*1000 + 10*60*1000),
    qr_code: "QR-ALICE-TECH",
    schemaVersion: "1.0",
    ticket_tier: "General Admission",
    check_in_method: "qr_code",
    location: { type: "Point", coordinates: [-121.8862, 37.3383] },
    metadata: { device_info: "iPhone", staff_verified: true },
    created_at: new Date()
  },
  {
    event_id: eventMusicId,
    user_id: userAliceId,
    venue_id: venue2Id,
    check_in_time: new Date(Date.now() + 14*24*60*60*1000 + 5*60*1000),
    qr_code: "QR-ALICE-MUSIC",
    schemaVersion: "1.0",
    ticket_tier: "General Admission",
    check_in_method: "mobile_app",
    location: { type: "Point", coordinates: [-97.7432, 30.2671] },
    created_at: new Date()
  },
  {
    event_id: eventMusicId,
    user_id: userBobId,
    venue_id: venue2Id,
    check_in_time: new Date(Date.now() + 14*24*60*60*1000 + 15*60*1000),
    qr_code: "QR-BOB-MUSIC",
    schemaVersion: "1.0",
    ticket_tier: "General Admission",
    check_in_method: "qr_code",
    location: { type: "Point", coordinates: [-97.7430, 30.2673] },
    created_at: new Date()
  }
]);


