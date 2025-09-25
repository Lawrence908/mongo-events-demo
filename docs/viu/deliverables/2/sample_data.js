// Insert realistic sample data demonstrating relationships

// Users
const userAliceId = ObjectId();
const userBobId = ObjectId();
db.users.insertMany([
  {
    _id: userAliceId,
    email: "alice@example.com",
    profile: { first_name: "Alice", last_name: "Nguyen", preferences: { categories: ["Technology", "Music"], radius_km: 25 } },
    created_at: new Date(),
    last_login: new Date()
  },
  {
    _id: userBobId,
    email: "bob@example.com",
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
    type: "Conference Center",
    description: "A conference center located in San Jose.",
    address: { street: "123 Main St", city: "San Jose", state: "CA", zip_code: "95112", country: "USA" },
    location: { type: "Point", coordinates: [-121.8863, 37.3382] },
    capacity: 800,
    amenities: ["WiFi", "Parking", "A/V"],
    contact: { phone: "(408) 555-1234", email: "info@grandcc.com", website: "https://grandcc.com" },
    pricing: { hourly_rate: 200, daily_rate: 1500, currency: "USD" },
    availability: { monday: { open: "09:00", close: "22:00" } },
    rating: 4.5,
    review_count: 12,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: venue2Id,
    name: "City Park - Austin",
    type: "Park",
    description: "Outdoor venue in Austin.",
    address: { street: "200 Park Ave", city: "Austin", state: "TX", zip_code: "73301", country: "USA" },
    location: { type: "Point", coordinates: [-97.7431, 30.2672] },
    capacity: 1500,
    amenities: ["Parking", "Outdoor Space"],
    contact: { phone: "(512) 555-2000", email: "contact@cityparkaustin.org", website: "https://cityparkaustin.org" },
    pricing: { hourly_rate: 50, daily_rate: 300, currency: "USD" },
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
    location: { type: "Point", coordinates: [-121.8863, 37.3382] },
    venueId: venue1Id,
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
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: eventMusicId,
    title: "Jazz Night Downtown",
    description: "Live jazz with local artists.",
    category: "Music",
    location: { type: "Point", coordinates: [-97.7431, 30.2672] },
    venueId: venue2Id,
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
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// Reviews (event and venue)
db.reviews.insertMany([
  { user_id: userAliceId, event_id: eventTechId, rating: 5, comment: "Fantastic content!", created_at: new Date(), updated_at: new Date() },
  { user_id: userBobId, venue_id: venue2Id, rating: 4, comment: "Great outdoor vibe", created_at: new Date(), updated_at: new Date() }
]);

// Check-ins (bridge demonstrates many:many)
db.checkins.insertMany([
  {
    event_id: eventTechId,
    user_id: userAliceId,
    venue_id: venue1Id,
    check_in_time: new Date(Date.now() + 7*24*60*60*1000 + 10*60*1000),
    qr_code: "QR-ALICE-TECH",
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
    ticket_tier: "General Admission",
    check_in_method: "qr_code",
    location: { type: "Point", coordinates: [-97.7430, 30.2673] },
    created_at: new Date()
  }
]);


