"""
MongoDB JSON Schema validation definitions for all collections.
This module provides comprehensive schema validation rules that enforce
data integrity, required fields, and coordinate bounds validation.
"""

from typing import Dict, Any


def get_events_schema() -> Dict[str, Any]:
    """JSON Schema validation for events collection"""
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["title", "category", "location", "startDate", "createdAt", "updatedAt"],
            "properties": {
                "title": {
                    "bsonType": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "Event title"
                },
                "description": {
                    "bsonType": ["string", "null"],
                    "maxLength": 1000,
                    "description": "Event description"
                },
                "category": {
                    "bsonType": "string",
                    "minLength": 1,
                    "maxLength": 50,
                    "description": "Event category"
                },
                "location": {
                    "bsonType": "object",
                    "required": ["type", "coordinates"],
                    "properties": {
                        "type": {
                            "enum": ["Point"],
                            "description": "GeoJSON type must be Point"
                        },
                        "coordinates": {
                            "bsonType": "array",
                            "items": {"bsonType": "double"},
                            "minItems": 2,
                            "maxItems": 2,
                            "description": "Longitude and latitude coordinates"
                        }
                    },
                    "additionalProperties": False,
                    "description": "GeoJSON Point location"
                },
                "address": {
                    "bsonType": ["object", "null"],
                    "properties": {
                        "street": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 200,
                            "description": "Street address"
                        },
                        "city": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100,
                            "description": "City name"
                        },
                        "state": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100,
                            "description": "State or province"
                        },
                        "zip": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 20,
                            "description": "ZIP or postal code"
                        },
                        "country": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100,
                            "description": "Country name"
                        }
                    },
                    "additionalProperties": False,
                    "description": "Event address information"
                },
                "directionsUrl": {
                    "bsonType": ["string", "null"],
                    "maxLength": 500,
                    "description": "Google Maps directions URL"
                },
                "venueId": {
                    "bsonType": ["objectId", "null"],
                    "description": "Reference to venues collection"
                },
                "startDate": {
                    "bsonType": "date",
                    "description": "Event start date and time"
                },
                "endDate": {
                    "bsonType": ["date", "null"],
                    "description": "Event end date and time"
                },
                "organizer": {
                    "bsonType": ["string", "null"],
                    "maxLength": 100,
                    "description": "Event organizer"
                },
                "maxAttendees": {
                    "bsonType": ["int", "null"],
                    "minimum": 1,
                    "description": "Maximum number of attendees"
                },
                "tickets": {
                    "bsonType": ["array", "null"],
                    "items": {
                        "bsonType": "object",
                        "required": ["tier", "price", "available", "sold"],
                        "properties": {
                            "tier": {
                                "bsonType": "string",
                                "minLength": 1,
                                "maxLength": 50
                            },
                            "price": {
                                "bsonType": "double",
                                "minimum": 0
                            },
                            "available": {
                                "bsonType": "int",
                                "minimum": 0
                            },
                            "sold": {
                                "bsonType": "int",
                                "minimum": 0
                            }
                        },
                        "additionalProperties": False
                    },
                    "description": "Embedded ticket information"
                },
                "attendees": {
                    "bsonType": ["array", "null"],
                    "items": {
                        "bsonType": "object",
                        "required": ["userId", "checkedIn"],
                        "properties": {
                            "userId": {
                                "bsonType": "objectId"
                            },
                            "checkedIn": {
                                "bsonType": "bool"
                            },
                            "checkInTime": {
                                "bsonType": ["date", "null"]
                            }
                        },
                        "additionalProperties": False
                    },
                    "description": "Embedded attendee information"
                },
                "tags": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "string",
                        "minLength": 1,
                        "maxLength": 50
                    },
                    "description": "Event tags for categorization"
                },
                "metadata": {
                    "bsonType": ["object", "null"],
                    "properties": {
                        "virtual": {"bsonType": "bool"},
                        "recurring": {"bsonType": "bool"},
                        "ageRestriction": {"bsonType": "string"},
                        "dressCode": {"bsonType": "string"}
                    },
                    "additionalProperties": True,
                    "description": "Flexible metadata for custom attributes"
                },
                "createdAt": {
                    "bsonType": "date",
                    "description": "Document creation timestamp"
                },
                "updatedAt": {
                    "bsonType": "date",
                    "description": "Last update timestamp"
                }
            },
            "additionalProperties": False,
            "patternProperties": {
                "^_id$": {
                    "bsonType": "objectId",
                    "description": "MongoDB ObjectId"
                }
            }
        }
    }


def get_venues_schema() -> Dict[str, Any]:
    """JSON Schema validation for venues collection"""
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "location", "address", "createdAt"],
            "properties": {
                "name": {
                    "bsonType": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "Venue name"
                },
                "address": {
                    "bsonType": "object",
                    "required": ["street", "city", "state", "zip", "country"],
                    "properties": {
                        "street": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 200
                        },
                        "city": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "state": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "zip": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 20
                        },
                        "country": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100
                        }
                    },
                    "additionalProperties": False,
                    "description": "Complete address information"
                },
                "location": {
                    "bsonType": "object",
                    "required": ["type", "coordinates"],
                    "properties": {
                        "type": {
                            "enum": ["Point"],
                            "description": "GeoJSON type must be Point"
                        },
                        "coordinates": {
                            "bsonType": "array",
                            "items": {"bsonType": "double"},
                            "minItems": 2,
                            "maxItems": 2,
                            "description": "Longitude and latitude coordinates"
                        }
                    },
                    "additionalProperties": False,
                    "description": "GeoJSON Point location"
                },
                "capacity": {
                    "bsonType": ["int", "null"],
                    "minimum": 1,
                    "description": "Venue capacity"
                },
                "amenities": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "string",
                        "minLength": 1,
                        "maxLength": 50
                    },
                    "description": "Available amenities"
                },
                "contact": {
                    "bsonType": ["object", "null"],
                    "properties": {
                        "phone": {
                            "bsonType": "string",
                            "maxLength": 20
                        },
                        "email": {
                            "bsonType": "string",
                            "maxLength": 255
                        },
                        "website": {
                            "bsonType": "string",
                            "maxLength": 500
                        }
                    },
                    "additionalProperties": False,
                    "description": "Contact information"
                },
                "createdAt": {
                    "bsonType": "date",
                    "description": "Document creation timestamp"
                }
            },
            "additionalProperties": False,
            "patternProperties": {
                "^_id$": {
                    "bsonType": "objectId",
                    "description": "MongoDB ObjectId"
                }
            }
        }
    }


def get_users_schema() -> Dict[str, Any]:
    """JSON Schema validation for users collection"""
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["email", "profile", "createdAt"],
            "properties": {
                "email": {
                    "bsonType": "string",
                    "minLength": 1,
                    "maxLength": 255,
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "description": "Unique email address"
                },
                "profile": {
                    "bsonType": "object",
                    "required": ["firstName", "lastName"],
                    "properties": {
                        "firstName": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "lastName": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "preferences": {
                            "bsonType": ["object", "null"],
                            "properties": {
                                "categories": {
                                    "bsonType": "array",
                                    "items": {
                                        "bsonType": "string",
                                        "minLength": 1,
                                        "maxLength": 50
                                    }
                                },
                                "location": {
                                    "bsonType": ["object", "null"],
                                    "required": ["type", "coordinates"],
                                    "properties": {
                                        "type": {
                                            "enum": ["Point"]
                                        },
                                        "coordinates": {
                                            "bsonType": "array",
                                            "items": {"bsonType": "double"},
                                            "minItems": 2,
                                            "maxItems": 2
                                        }
                                    },
                                    "additionalProperties": False
                                },
                                "radiusKm": {
                                    "bsonType": ["double", "null"],
                                    "minimum": 0.1,
                                    "maximum": 1000
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False,
                    "description": "User profile information"
                },
                "createdAt": {
                    "bsonType": "date",
                    "description": "Account creation timestamp"
                },
                "lastLogin": {
                    "bsonType": ["date", "null"],
                    "description": "Last login timestamp"
                }
            },
            "additionalProperties": False,
            "patternProperties": {
                "^_id$": {
                    "bsonType": "objectId",
                    "description": "MongoDB ObjectId"
                }
            }
        }
    }


def get_checkins_schema() -> Dict[str, Any]:
    """JSON Schema validation for checkins collection"""
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["eventId", "userId", "venueId", "checkInTime", "qrCode", "createdAt"],
            "properties": {
                "eventId": {
                    "bsonType": "objectId",
                    "description": "Reference to events collection"
                },
                "userId": {
                    "bsonType": "objectId",
                    "description": "Reference to users collection"
                },
                "venueId": {
                    "bsonType": "objectId",
                    "description": "Reference to venues collection (denormalized for analytics)"
                },
                "checkInTime": {
                    "bsonType": "date",
                    "description": "Check-in timestamp"
                },
                "qrCode": {
                    "bsonType": "string",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "Unique QR code for check-in"
                },
                "ticketTier": {
                    "bsonType": ["string", "null"],
                    "maxLength": 50,
                    "description": "Ticket tier used for check-in"
                },
                "checkInMethod": {
                    "bsonType": ["string", "null"],
                    "maxLength": 50,
                    "enum": ["qrCode", "manual", "mobileApp", None],
                    "description": "Method used for check-in"
                },
                "location": {
                    "bsonType": ["object", "null"],
                    "required": ["type", "coordinates"],
                    "properties": {
                        "type": {
                            "enum": ["Point"],
                            "description": "GeoJSON type must be Point"
                        },
                        "coordinates": {
                            "bsonType": "array",
                            "items": {"bsonType": "double"},
                            "minItems": 2,
                            "maxItems": 2,
                            "description": "Longitude and latitude coordinates"
                        }
                    },
                    "additionalProperties": False,
                    "description": "Check-in location (if different from event)"
                },
                "metadata": {
                    "bsonType": ["object", "null"],
                    "properties": {
                        "deviceInfo": {
                            "bsonType": ["string", "null"],
                            "maxLength": 200,
                            "description": "Mobile device or browser info"
                        },
                        "ipAddress": {
                            "bsonType": ["string", "null"],
                            "maxLength": 45,
                            "pattern": "^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
                            "description": "IP address for security/analytics"
                        },
                        "staffVerified": {
                            "bsonType": ["bool", "null"],
                            "description": "Manual verification by staff"
                        }
                    },
                    "additionalProperties": False,
                    "description": "Additional check-in context"
                },
                "createdAt": {
                    "bsonType": "date",
                    "description": "Record creation timestamp"
                }
            },
            "additionalProperties": False,
            "patternProperties": {
                "^_id$": {
                    "bsonType": "objectId",
                    "description": "MongoDB ObjectId"
                }
            }
        }
    }


def validate_coordinate_bounds(coordinates: list[float]) -> bool:
    """
    Validate that coordinates are within valid bounds.
    
    Args:
        coordinates: [longitude, latitude] pair
        
    Returns:
        True if coordinates are valid, False otherwise
        
    Raises:
        ValueError: If coordinates are out of bounds
    """
    if len(coordinates) != 2:
        raise ValueError("Coordinates must be [longitude, latitude]")
    
    longitude, latitude = coordinates
    
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude {longitude} must be between -180 and 180")
    
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude {latitude} must be between -90 and 90")
    
    return True


def get_reviews_schema() -> Dict[str, Any]:
    """JSON Schema validation for reviews collection"""
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["userId", "rating", "createdAt", "updatedAt"],
            "properties": {
                "eventId": {
                    "bsonType": ["objectId", "null"],
                    "description": "Reference to events collection (if reviewing event)"
                },
                "venueId": {
                    "bsonType": ["objectId", "null"],
                    "description": "Reference to venues collection (if reviewing venue)"
                },
                "userId": {
                    "bsonType": "objectId",
                    "description": "Reference to users collection"
                },
                "rating": {
                    "bsonType": "int",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Rating from 1 to 5 stars"
                },
                "comment": {
                    "bsonType": "string",
                    "minLength": 1,
                    "maxLength": 1000,
                    "description": "Review comment text"
                },
                "createdAt": {
                    "bsonType": "date",
                    "description": "Review creation timestamp"
                },
                "updatedAt": {
                    "bsonType": ["date", "null"],
                    "description": "Last update timestamp"
                }
            },
            "additionalProperties": False,
            "patternProperties": {
                "^_id$": {
                    "bsonType": "objectId",
                    "description": "MongoDB ObjectId"
                }
            }
        }
    }


def get_all_schemas() -> Dict[str, Dict[str, Any]]:
    """Get all collection schemas as a dictionary"""
    return {
        "events": get_events_schema(),
        "venues": get_venues_schema(),
        "users": get_users_schema(),
        "checkins": get_checkins_schema(),
        "reviews": get_reviews_schema()
    }
