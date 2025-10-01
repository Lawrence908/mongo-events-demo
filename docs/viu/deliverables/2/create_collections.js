// Create collections with JSON Schema validators for EventSphere

// Events
db.createCollection("events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "title",
        "category",
        "location",
        "start_date",
        "event_type",
        "schemaVersion",
        "created_at",
        "updated_at"
      ],
      properties: {
        title: { bsonType: "string", minLength: 1, maxLength: 200 },
        description: { bsonType: ["string", "null"] },
        category: { bsonType: "string", minLength: 1 },
        event_type: { bsonType: "string", enum: ["in_person", "virtual", "hybrid", "recurring"] },
        schemaVersion: { bsonType: "string", enum: ["1.0"] },
        location: {
          bsonType: "object",
          required: ["type", "coordinates"],
          properties: {
            type: { enum: ["Point"] },
            coordinates: {
              bsonType: "array",
              items: { bsonType: "double" },
              minItems: 2,
              maxItems: 2
            }
          }
        },
        venueId: { bsonType: ["objectId", "null"] },
        venue_reference: {
          bsonType: ["object", "null"],
          properties: {
            name: { bsonType: ["string", "null"] },
            city: { bsonType: ["string", "null"] },
            capacity: { bsonType: ["int", "long", "null"], minimum: 0 },
            venue_type: { bsonType: ["string", "null"] }
          }
        },
        start_date: { bsonType: "date" },
        end_date: { bsonType: ["date", "null"] },
        organizer: { bsonType: ["string", "null"] },
        max_attendees: { bsonType: ["int", "long", "null"], minimum: 1 },
        current_attendees: { bsonType: ["int", "long", "null"], minimum: 0 },
        price: { bsonType: ["double", "int", "long", "null"], minimum: 0 },
        currency: { bsonType: ["string", "null"] },
        is_free: { bsonType: ["bool", "null"] },
        status: { bsonType: ["string", "null"], enum: ["draft", "published", "cancelled", "completed", null] },
        tickets: {
          bsonType: ["array", "null"],
          items: {
            bsonType: "object",
            required: ["tier", "price", "available", "sold"],
            properties: {
              tier: { bsonType: "string" },
              price: { bsonType: ["double", "int", "long"], minimum: 0 },
              available: { bsonType: ["int", "long"], minimum: 0 },
              sold: { bsonType: ["int", "long"], minimum: 0 }
            }
          }
        },
        attendees: {
          bsonType: ["array", "null"],
          items: {
            bsonType: "object",
            required: ["user_id", "checked_in"],
            properties: {
              user_id: { bsonType: "objectId" },
              checked_in: { bsonType: "bool" },
              check_in_time: { bsonType: ["date", "null"] }
            }
          }
        },
        tags: { bsonType: ["array", "null"], items: { bsonType: "string" } },
        // Polymorphic event-specific fields
        virtual_details: {
          bsonType: ["object", "null"],
          properties: {
            platform: { bsonType: ["string", "null"] },
            meeting_url: { bsonType: ["string", "null"] },
            recording_available: { bsonType: ["bool", "null"] },
            timezone: { bsonType: ["string", "null"] }
          }
        },
        recurring_details: {
          bsonType: ["object", "null"],
          properties: {
            frequency: { bsonType: ["string", "null"], enum: ["daily", "weekly", "monthly", "yearly", null] },
            end_recurrence: { bsonType: ["date", "null"] },
            exceptions: { bsonType: ["array", "null"], items: { bsonType: "date" } }
          }
        },
        hybrid_details: {
          bsonType: ["object", "null"],
          properties: {
            virtual_capacity: { bsonType: ["int", "long", "null"], minimum: 0 },
            in_person_capacity: { bsonType: ["int", "long", "null"], minimum: 0 },
            virtual_meeting_url: { bsonType: ["string", "null"] }
          }
        },
        metadata: {
          bsonType: ["object", "null"],
          properties: {
            age_restriction: { bsonType: ["string", "null"] },
            dress_code: { bsonType: ["string", "null"] },
            accessibility_features: { bsonType: ["array", "null"], items: { bsonType: "string" } }
          }
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

// Venues
db.createCollection("venues", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "address", "location", "venue_type", "schemaVersion", "created_at", "updated_at"],
      properties: {
        name: { bsonType: "string", minLength: 1 },
        venue_type: { bsonType: "string", enum: ["conference_center", "park", "restaurant", "virtual_space", "stadium", "theater"] },
        schemaVersion: { bsonType: "string", enum: ["1.0"] },
        type: { bsonType: ["string", "null"] },
        description: { bsonType: ["string", "null"] },
        address: {
          bsonType: "object",
          required: ["street", "city", "state", "zip_code", "country"],
          properties: {
            street: { bsonType: "string" },
            city: { bsonType: "string" },
            state: { bsonType: "string" },
            zip_code: { bsonType: "string" },
            country: { bsonType: "string" }
          }
        },
        location: {
          bsonType: "object",
          required: ["type", "coordinates"],
          properties: {
            type: { enum: ["Point"] },
            coordinates: {
              bsonType: "array",
              items: { bsonType: "double" },
              minItems: 2,
              maxItems: 2
            }
          }
        },
        capacity: { bsonType: ["int", "long", "null"], minimum: 0 },
        amenities: { bsonType: ["array", "null"], items: { bsonType: "string" } },
        contact: {
          bsonType: ["object", "null"],
          properties: { phone: { bsonType: ["string", "null"] }, email: { bsonType: ["string", "null"] }, website: { bsonType: ["string", "null"] } }
        },
        pricing: {
          bsonType: ["object", "null"],
          properties: { hourly_rate: { bsonType: ["double", "int", "long", "null"], minimum: 0 }, daily_rate: { bsonType: ["double", "int", "long", "null"], minimum: 0 }, currency: { bsonType: ["string", "null"] } }
        },
        availability: { bsonType: ["object", "null"] },
        // Polymorphic venue-specific fields
        conference_center_details: {
          bsonType: ["object", "null"],
          properties: {
            breakout_rooms: { bsonType: ["int", "long", "null"], minimum: 0 },
            a_v_equipment: { bsonType: ["array", "null"], items: { bsonType: "string" } },
            catering_available: { bsonType: ["bool", "null"] }
          }
        },
        park_details: {
          bsonType: ["object", "null"],
          properties: {
            outdoor_space: { bsonType: ["bool", "null"] },
            parking_spaces: { bsonType: ["int", "long", "null"], minimum: 0 },
            restroom_facilities: { bsonType: ["bool", "null"] }
          }
        },
        virtual_space_details: {
          bsonType: ["object", "null"],
          properties: {
            platform: { bsonType: ["string", "null"] },
            max_concurrent_users: { bsonType: ["int", "long", "null"], minimum: 0 },
            recording_capability: { bsonType: ["bool", "null"] }
          }
        },
        rating: { bsonType: ["double", "int", "long", "null"], minimum: 0, maximum: 5 },
        review_count: { bsonType: ["int", "long", "null"], minimum: 0 },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

// Users
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "profile", "schemaVersion", "created_at"],
      properties: {
        email: { bsonType: "string", minLength: 3 },
        schemaVersion: { bsonType: "string", enum: ["1.0"] },
        profile: {
          bsonType: "object",
          required: ["first_name", "last_name"],
          properties: {
            first_name: { bsonType: "string" },
            last_name: { bsonType: "string" },
            preferences: {
              bsonType: ["object", "null"],
              properties: {
                categories: { bsonType: ["array", "null"], items: { bsonType: "string" } },
                location: {
                  bsonType: ["object", "null"],
                  properties: {
                    type: { enum: ["Point", null] },
                    coordinates: { bsonType: ["array", "null"], items: { bsonType: "double" }, minItems: 2, maxItems: 2 }
                  }
                },
                radius_km: { bsonType: ["double", "int", "long", "null"], minimum: 0 }
              }
            }
          }
        },
        created_at: { bsonType: "date" },
        last_login: { bsonType: ["date", "null"] }
      }
    }
  }
});

// Check-ins (bridge)
db.createCollection("checkins", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["event_id", "user_id", "venue_id", "check_in_time", "qr_code", "schemaVersion", "created_at"],
      properties: {
        event_id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        venue_id: { bsonType: "objectId" },
        check_in_time: { bsonType: "date" },
        qr_code: { bsonType: "string", minLength: 3 },
        schemaVersion: { bsonType: "string", enum: ["1.0"] },
        ticket_tier: { bsonType: ["string", "null"] },
        check_in_method: { bsonType: ["string", "null"], enum: ["qr_code", "manual", "mobile_app", null] },
        location: {
          bsonType: ["object", "null"],
          properties: {
            type: { enum: ["Point", null] },
            coordinates: { bsonType: ["array", "null"], items: { bsonType: "double" }, minItems: 2, maxItems: 2 }
          }
        },
        metadata: { bsonType: ["object", "null"], properties: { device_info: { bsonType: ["string", "null"] }, ip_address: { bsonType: ["string", "null"] }, staff_verified: { bsonType: ["bool", "null"] } } },
        created_at: { bsonType: "date" }
      }
    }
  }
});

// Reviews
db.createCollection("reviews", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "rating", "schemaVersion", "created_at"],
      properties: {
        event_id: { bsonType: ["objectId", "null"] },
        venue_id: { bsonType: ["objectId", "null"] },
        user_id: { bsonType: "objectId" },
        rating: { bsonType: ["int", "long"], minimum: 1, maximum: 5 },
        schemaVersion: { bsonType: "string", enum: ["1.0"] },
        comment: { bsonType: ["string", "null"] },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: ["date", "null"] }
      }
    }
  }
});


