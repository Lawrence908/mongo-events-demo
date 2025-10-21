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
                "startDate",
                "eventType",
                "schemaVersion",
                "createdAt",
                "updatedAt"
            ],
            properties: {
                title: { bsonType: "string", minLength: 1, maxLength: 200 },
                description: { bsonType: ["string", "null"] },
                category: { bsonType: "string", minLength: 1 },
                eventType: { bsonType: "string", enum: ["inPerson", "virtual", "hybrid", "recurring"] },
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
                venueReference: {
                    bsonType: ["object", "null"],
                    properties: {
                        name: { bsonType: ["string", "null"] },
                        city: { bsonType: ["string", "null"] },
                        capacity: { bsonType: ["int", "long", "null"], minimum: 0 },
                        venueType: { bsonType: ["string", "null"] }
                    }
                },
                startDate: { bsonType: "date" },
                endDate: { bsonType: ["date", "null"] },
                organizer: { bsonType: ["string", "null"] },
                maxAttendees: { bsonType: ["int", "long", "null"], minimum: 1 },
                currentAttendees: { bsonType: ["int", "long", "null"], minimum: 0 },
                price: { bsonType: ["double", "int", "long", "null"], minimum: 0 },
                currency: { bsonType: ["string", "null"] },
                isFree: { bsonType: ["bool", "null"] },
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
                        required: ["userId", "checkedIn"],
                        properties: {
                            userId: { bsonType: "objectId" },
                            checkedIn: { bsonType: "bool" },
                            checkInTime: { bsonType: ["date", "null"] }
                        }
                    }
                },
                tags: { bsonType: ["array", "null"], items: { bsonType: "string" } },
                // Polymorphic event-specific fields
                virtualDetails: {
                    bsonType: ["object", "null"],
                    properties: {
                        platform: { bsonType: ["string", "null"] },
                        meetingUrl: { bsonType: ["string", "null"] },
                        recordingAvailable: { bsonType: ["bool", "null"] },
                        timezone: { bsonType: ["string", "null"] }
                    }
                },
                recurringDetails: {
                    bsonType: ["object", "null"],
                    properties: {
                        frequency: { bsonType: ["string", "null"], enum: ["daily", "weekly", "monthly", "yearly", null] },
                        endRecurrence: { bsonType: ["date", "null"] },
                        exceptions: { bsonType: ["array", "null"], items: { bsonType: "date" } }
                    }
                },
                hybridDetails: {
                    bsonType: ["object", "null"],
                    properties: {
                        virtualCapacity: { bsonType: ["int", "long", "null"], minimum: 0 },
                        inPersonCapacity: { bsonType: ["int", "long", "null"], minimum: 0 },
                        virtual_meetingUrl: { bsonType: ["string", "null"] }
                    }
                },
                metadata: {
                    bsonType: ["object", "null"],
                    properties: {
                        ageRestriction: { bsonType: ["string", "null"] },
                        dressCode: { bsonType: ["string", "null"] },
                        accessibilityFeatures: { bsonType: ["array", "null"], items: { bsonType: "string" } }
                    }
                },
                computedStats: {
                    bsonType: ["object", "null"],
                    properties: {
                        totalTicketsSold: { bsonType: ["int", "long", "null"], minimum: 0 },
                        totalRevenue: { bsonType: ["double", "int", "long", "null"], minimum: 0 },
                        attendanceRate: { bsonType: ["double", "null"], minimum: 0, maximum: 100 },
                        reviewCount: { bsonType: ["int", "long", "null"], minimum: 0 },
                        averageRating: { bsonType: ["double", "null"], minimum: 0, maximum: 5 },
                        lastUpdated: { bsonType: ["date", "null"] }
                    }
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// Venues
db.createCollection("venues", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["name", "address", "location", "venueType", "schemaVersion", "createdAt", "updatedAt"],
            properties: {
                name: { bsonType: "string", minLength: 1 },
                venueType: { bsonType: "string", enum: ["conferenceCenter", "park", "restaurant", "virtualSpace", "stadium", "theater"] },
                schemaVersion: { bsonType: "string", enum: ["1.0"] },
                type: { bsonType: ["string", "null"] },
                description: { bsonType: ["string", "null"] },
                address: {
                    bsonType: "object",
                    required: ["street", "city", "state", "zipCode", "country"],
                    properties: {
                        street: { bsonType: "string" },
                        city: { bsonType: "string" },
                        state: { bsonType: "string" },
                        zipCode: { bsonType: "string" },
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
                    properties: { hourlyRate: { bsonType: ["double", "int", "long", "null"], minimum: 0 }, dailyRate: { bsonType: ["double", "int", "long", "null"], minimum: 0 }, currency: { bsonType: ["string", "null"] } }
                },
                availability: { bsonType: ["object", "null"] },
                // Polymorphic venue-specific fields
                conferenceCenterDetails: {
                    bsonType: ["object", "null"],
                    properties: {
                        breakoutRooms: { bsonType: ["int", "long", "null"], minimum: 0 },
                        avEquipment: { bsonType: ["array", "null"], items: { bsonType: "string" } },
                        cateringAvailable: { bsonType: ["bool", "null"] }
                    }
                },
                parkDetails: {
                    bsonType: ["object", "null"],
                    properties: {
                        outdoorSpace: { bsonType: ["bool", "null"] },
                        parkingSpaces: { bsonType: ["int", "long", "null"], minimum: 0 },
                        restroomFacilities: { bsonType: ["bool", "null"] }
                    }
                },
                virtualSpaceDetails: {
                    bsonType: ["object", "null"],
                    properties: {
                        platform: { bsonType: ["string", "null"] },
                        maxConcurrentUsers: { bsonType: ["int", "long", "null"], minimum: 0 },
                        recordingCapability: { bsonType: ["bool", "null"] }
                    }
                },
                rating: { bsonType: ["double", "int", "long", "null"], minimum: 0, maximum: 5 },
                reviewCount: { bsonType: ["int", "long", "null"], minimum: 0 },
                computedStats: {
                    bsonType: ["object", "null"],
                    properties: {
                        totalEventsHosted: { bsonType: ["int", "long", "null"], minimum: 0 },
                        averageAttendance: { bsonType: ["int", "long", "null"], minimum: 0 },
                        revenueGenerated: { bsonType: ["double", "int", "long", "null"], minimum: 0 },
                        lastEventDate: { bsonType: ["date", "null"] },
                        lastUpdated: { bsonType: ["date", "null"] }
                    }
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: "date" }
            }
        }
    }
});

// Users
db.createCollection("users", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["email", "profile", "schemaVersion", "createdAt"],
            properties: {
                email: { bsonType: "string", minLength: 3 },
                schemaVersion: { bsonType: "string", enum: ["1.0"] },
                profile: {
                    bsonType: "object",
                    required: ["firstName", "lastName"],
                    properties: {
                        firstName: { bsonType: "string" },
                        lastName: { bsonType: "string" },
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
                                radiusKm: { bsonType: ["double", "int", "long", "null"], minimum: 0 }
                            }
                        }
                    }
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] },
                lastLogin: { bsonType: ["date", "null"] }
            }
        }
    }
});

// Reviews
db.createCollection("reviews", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["userId", "rating", "schemaVersion", "createdAt"],
            properties: {
                eventId: { bsonType: ["objectId", "null"] },
                venueId: { bsonType: ["objectId", "null"] },
                userId: { bsonType: "objectId" },
                rating: { bsonType: ["int", "long"], minimum: 1, maximum: 5 },
                schemaVersion: { bsonType: "string", enum: ["1.0"] },
                comment: { bsonType: ["string", "null"] },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// Check-ins (bridge)
db.createCollection("checkins", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["eventId", "userId", "venueId", "checkInTime", "qrCode", "schemaVersion", "createdAt"],
            properties: {
                eventId: { bsonType: "objectId" },
                userId: { bsonType: "objectId" },
                venueId: { bsonType: "objectId" },
                checkInTime: { bsonType: "date" },
                qrCode: { bsonType: "string", minLength: 3 },
                schemaVersion: { bsonType: "string", enum: ["1.0"] },
                ticketTier: { bsonType: ["string", "null"] },
                checkInMethod: { bsonType: ["string", "null"], enum: ["qrCode", "manual", "mobileApp", null] },
                location: {
                    bsonType: ["object", "null"],
                    properties: {
                        type: { enum: ["Point", null] },
                        coordinates: { bsonType: ["array", "null"], items: { bsonType: "double" }, minItems: 2, maxItems: 2 }
                    }
                },
                metadata: { bsonType: ["object", "null"], properties: { deviceInfo: { bsonType: ["string", "null"] }, ipAddress: { bsonType: ["string", "null"] }, staffVerified: { bsonType: ["bool", "null"] } } },
                createdAt: { bsonType: "date" }
            }
        }
    }
});

