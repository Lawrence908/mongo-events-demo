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
        "created_at",
        "updated_at"
      ],
      properties: {
        title: { bsonType: "string", minLength: 1, maxLength: 200 },
        description: { bsonType: ["string", "null"] },
        category: { bsonType: "string", minLength: 1 },
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
        metadata: {
          bsonType: ["object", "null"],
          properties: {
            virtual: { bsonType: ["bool", "null"] },
            recurring: { bsonType: ["bool", "null"] },
            age_restriction: { bsonType: ["string", "null"] },
            dress_code: { bsonType: ["string", "null"] }
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
      required: ["name", "address", "location", "created_at", "updated_at"],
      properties: {
        name: { bsonType: "string", minLength: 1 },
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
      required: ["email", "profile", "created_at"],
      properties: {
        email: { bsonType: "string", minLength: 3 },
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
      required: ["event_id", "user_id", "venue_id", "check_in_time", "qr_code", "created_at"],
      properties: {
        event_id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        venue_id: { bsonType: "objectId" },
        check_in_time: { bsonType: "date" },
        qr_code: { bsonType: "string", minLength: 3 },
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
      required: ["user_id", "rating", "created_at"],
      properties: {
        event_id: { bsonType: ["objectId", "null"] },
        venue_id: { bsonType: ["objectId", "null"] },
        user_id: { bsonType: "objectId" },
        rating: { bsonType: ["int", "long"], minimum: 1, maximum: 5 },
        comment: { bsonType: ["string", "null"] },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: ["date", "null"] }
      }
    }
  }
});


