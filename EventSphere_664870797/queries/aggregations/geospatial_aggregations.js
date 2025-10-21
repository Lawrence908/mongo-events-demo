// Geospatial Aggregation Pipelines for EventSphere
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("=".repeat(60));
print("GEOSPATIAL AGGREGATION PIPELINES");
print("=".repeat(60));

// ===== 1. NEARBY EVENTS DISCOVERY =====
print("\n1. NEARBY EVENTS DISCOVERY");
print("-".repeat(40));

// Find events within 50km of Vancouver downtown
print("Finding events within 50km of Vancouver downtown:");
db.events.aggregate([
    {
        $geoNear: {
            near: { type: "Point", coordinates: [-123.1207, 49.2827] }, // Vancouver downtown
            distanceField: "distance",
            maxDistance: 50000, // 50km in meters
            spherical: true,
            query: { status: "published" } // Only published events
        }
    },
    {
        $project: {
            title: 1,
            category: 1,
            eventType: 1,
            startDate: 1,
            price: 1,
            "venueReference.name": 1,
            "venueReference.city": 1,
            distance: { $round: [{ $divide: ["$distance", 1000] }, 2] } // Convert to km
        }
    },
    {
        $sort: { distance: 1, startDate: 1 }
    },
    {
        $limit: 10
    }
]).forEach(event => {
    const venue = event.venueReference?.name || "Custom Location";
    const city = event.venueReference?.city || "Unknown";
    print(`- ${event.title} (${event.category}) - ${event.distance}km away`);
    print(`  Venue: ${venue}, ${city} - $${event.price || 0} CAD`);
    print(`  Date: ${event.startDate.toISOString().split('T')[0]} - Type: ${event.eventType}`);
});

// ===== 2. EVENTS BY DISTANCE RANGES =====
print("\n2. EVENTS BY DISTANCE RANGES");
print("-".repeat(40));

// Group events by distance ranges from Vancouver
print("Grouping events by distance ranges from Vancouver:");
db.events.aggregate([
    {
        $geoNear: {
            near: { type: "Point", coordinates: [-123.1207, 49.2827] },
            distanceField: "distance",
            spherical: true,
            query: { status: "published" }
        }
    },
    {
        $addFields: {
            distanceKm: { $divide: ["$distance", 1000] },
            distanceRange: {
                $switch: {
                    branches: [
                        { case: { $lte: [{ $divide: ["$distance", 1000] }, 10] }, then: "0-10km" },
                        { case: { $lte: [{ $divide: ["$distance", 1000] }, 25] }, then: "10-25km" },
                        { case: { $lte: [{ $divide: ["$distance", 1000] }, 50] }, then: "25-50km" },
                        { case: { $lte: [{ $divide: ["$distance", 1000] }, 100] }, then: "50-100km" }
                    ],
                    default: "100km+"
                }
            }
        }
    },
    {
        $group: {
            _id: "$distanceRange",
            eventCount: { $sum: 1 },
            categories: { $addToSet: "$category" },
            avgPrice: { $avg: "$price" },
            freeEvents: { $sum: { $cond: [{ $eq: ["$isFree", true] }, 1, 0] } }
        }
    },
    {
        $sort: { _id: 1 }
    }
]).forEach(range => {
    print(`${range._id}:`);
    print(`  Events: ${range.eventCount}`);
    print(`  Categories: ${range.categories.join(', ')}`);
    print(`  Avg Price: $${range.avgPrice ? range.avgPrice.toFixed(2) : 0} CAD`);
    print(`  Free Events: ${range.freeEvents}`);
});

// ===== 3. VENUE PROXIMITY ANALYSIS =====
print("\n3. VENUE PROXIMITY ANALYSIS");
print("-".repeat(40));

// Find venues near popular event locations
print("Finding venues near high-activity event areas:");
db.venues.aggregate([
    {
        $geoNear: {
            near: { type: "Point", coordinates: [-123.1207, 49.2827] }, // Vancouver downtown
            distanceField: "distanceFromCenter",
            spherical: true,
            maxDistance: 25000 // 25km radius
        }
    },
    {
        $lookup: {
            from: "events",
            let: { venueId: "$_id" },
            pipeline: [
                { $match: { $expr: { $eq: ["$venueId", "$$venueId"] } } },
                { $count: "eventCount" }
            ],
            as: "eventStats"
        }
    },
    {
        $addFields: {
            totalEvents: { $ifNull: [{ $arrayElemAt: ["$eventStats.eventCount", 0] }, 0] },
            distanceKm: { $round: [{ $divide: ["$distanceFromCenter", 1000] }, 2] }
        }
    },
    {
        $match: { totalEvents: { $gt: 0 } } // Only venues with events
    },
    {
        $project: {
            name: 1,
            venueType: 1,
            capacity: 1,
            rating: 1,
            "address.city": 1,
            distanceKm: 1,
            totalEvents: 1,
            eventsPerKm: { $round: [{ $divide: ["$totalEvents", "$distanceKm"] }, 2] }
        }
    },
    {
        $sort: { totalEvents: -1, distanceKm: 1 }
    }
]).forEach(venue => {
    print(`- ${venue.name} (${venue.venueType})`);
    print(`  Distance: ${venue.distanceKm}km - Events: ${venue.totalEvents}`);
    print(`  Capacity: ${venue.capacity} - Rating: ${venue.rating || 'N/A'}`);
    print(`  Events/km ratio: ${venue.eventsPerKm}`);
});

// ===== 4. USER LOCATION PREFERENCES =====
print("\n4. USER LOCATION PREFERENCES");
print("-".repeat(40));

// Analyze user preferences by geographic clusters
print("Analyzing user location preferences:");
db.users.aggregate([
    {
        $match: {
            "profile.preferences.location": { $exists: true }
        }
    },
    {
        $addFields: {
            locationArea: {
                $switch: {
                    branches: [
                        {
                            case: {
                                $and: [
                                    { $gte: ["$profile.preferences.location.coordinates.0", -123.3] },
                                    { $lte: ["$profile.preferences.location.coordinates.0", -123.0] },
                                    { $gte: ["$profile.preferences.location.coordinates.1", 49.2] },
                                    { $lte: ["$profile.preferences.location.coordinates.1", 49.3] }
                                ]
                            },
                            then: "Vancouver Metro"
                        },
                        {
                            case: {
                                $and: [
                                    { $gte: ["$profile.preferences.location.coordinates.0", -124.1] },
                                    { $lte: ["$profile.preferences.location.coordinates.0", -123.8] },
                                    { $gte: ["$profile.preferences.location.coordinates.1", 49.0] },
                                    { $lte: ["$profile.preferences.location.coordinates.1", 49.2] }
                                ]
                            },
                            then: "Nanaimo Area"
                        }
                    ],
                    default: "Other BC"
                }
            }
        }
    },
    {
        $group: {
            _id: "$locationArea",
            userCount: { $sum: 1 },
            avgRadius: { $avg: "$profile.preferences.radiusKm" },
            preferredCategories: { $push: "$profile.preferences.categories" },
            maxRadius: { $max: "$profile.preferences.radiusKm" },
            minRadius: { $min: "$profile.preferences.radiusKm" }
        }
    },
    {
        $addFields: {
            topCategories: {
                $slice: [
                    {
                        $map: {
                            input: {
                                $setIntersection: [
                                    { $reduce: {
                                        input: "$preferredCategories",
                                        initialValue: [],
                                        in: { $concatArrays: ["$$value", "$$this"] }
                                    }}
                                ]
                            },
                            as: "category",
                            in: "$$category"
                        }
                    },
                    5
                ]
            }
        }
    }
]).forEach(area => {
    print(`${area._id}:`);
    print(`  Users: ${area.userCount}`);
    print(`  Avg Search Radius: ${area.avgRadius.toFixed(1)}km`);
    print(`  Radius Range: ${area.minRadius}-${area.maxRadius}km`);
    print(`  Popular Categories: ${area.topCategories.join(', ')}`);
});

// ===== 5. GEOSPATIAL EVENT DENSITY =====
print("\n5. GEOSPATIAL EVENT DENSITY");
print("-".repeat(40));

// Calculate event density in different geographic areas
print("Calculating event density by geographic grid:");
db.events.aggregate([
    {
        $match: {
            status: "published",
            location: { $exists: true }
        }
    },
    {
        $addFields: {
            // Create a grid system (0.1 degree squares ≈ 11km squares)
            gridLat: { $floor: { $multiply: ["$location.coordinates.1", 10] } },
            gridLng: { $floor: { $multiply: ["$location.coordinates.0", 10] } }
        }
    },
    {
        $group: {
            _id: {
                lat: "$gridLat",
                lng: "$gridLng"
            },
            eventCount: { $sum: 1 },
            categories: { $addToSet: "$category" },
            eventTypes: { $addToSet: "$eventType" },
            avgPrice: { $avg: "$price" },
            freeEventCount: { $sum: { $cond: [{ $eq: ["$isFree", true] }, 1, 0] } },
            sampleEvents: { $push: { title: "$title", category: "$category" } }
        }
    },
    {
        $addFields: {
            centerLat: { $divide: ["$_id.lat", 10] },
            centerLng: { $divide: ["$_id.lng", 10] },
            freeEventPercentage: { 
                $multiply: [
                    { $divide: ["$freeEventCount", "$eventCount"] }, 
                    100
                ]
            }
        }
    },
    {
        $match: { eventCount: { $gte: 2 } } // Only show areas with multiple events
    },
    {
        $sort: { eventCount: -1 }
    },
    {
        $limit: 5
    }
]).forEach(grid => {
    print(`Grid Area (${grid.centerLat.toFixed(2)}, ${grid.centerLng.toFixed(2)}):`);
    print(`  Events: ${grid.eventCount}`);
    print(`  Categories: ${grid.categories.join(', ')}`);
    print(`  Event Types: ${grid.eventTypes.join(', ')}`);
    print(`  Avg Price: $${grid.avgPrice ? grid.avgPrice.toFixed(2) : 0} CAD`);
    print(`  Free Events: ${grid.freeEventPercentage.toFixed(1)}%`);
    print(`  Sample Events: ${grid.sampleEvents.slice(0, 2).map(e => e.title).join(', ')}`);
});

// ===== 6. TRAVEL DISTANCE ANALYSIS =====
print("\n6. TRAVEL DISTANCE ANALYSIS");
print("-".repeat(40));

// Analyze how far users are willing to travel for different event types
print("Analyzing user travel patterns for events:");
db.users.aggregate([
    {
        $match: {
            "profile.preferences.location": { $exists: true },
            "profile.preferences.radiusKm": { $exists: true }
        }
    },
    {
        $lookup: {
            from: "checkins",
            localField: "_id",
            foreignField: "userId",
            as: "checkins"
        }
    },
    {
        $unwind: "$checkins"
    },
    {
        $lookup: {
            from: "events",
            localField: "checkins.eventId",
            foreignField: "_id",
            as: "attendedEvent"
        }
    },
    {
        $unwind: "$attendedEvent"
    },
    {
        $addFields: {
            actualDistance: {
                $multiply: [
                    {
                        $sqrt: {
                            $add: [
                                {
                                    $pow: [
                                        {
                                            $subtract: [
                                                "$profile.preferences.location.coordinates.0",
                                                "$attendedEvent.location.coordinates.0"
                                            ]
                                        },
                                        2
                                    ]
                                },
                                {
                                    $pow: [
                                        {
                                            $subtract: [
                                                "$profile.preferences.location.coordinates.1",
                                                "$attendedEvent.location.coordinates.1"
                                            ]
                                        },
                                        2
                                    ]
                                }
                            ]
                        }
                    },
                    111 // Approximate km per degree
                ]
            }
        }
    },
    {
        $group: {
            _id: "$attendedEvent.category",
            avgTravelDistance: { $avg: "$actualDistance" },
            maxTravelDistance: { $max: "$actualDistance" },
            avgPreferredRadius: { $avg: "$profile.preferences.radiusKm" },
            attendeeCount: { $sum: 1 }
        }
    },
    {
        $addFields: {
            travelVsPreference: {
                $divide: ["$avgTravelDistance", "$avgPreferredRadius"]
            }
        }
    },
    {
        $sort: { avgTravelDistance: -1 }
    }
]).forEach(category => {
    print(`${category._id}:`);
    print(`  Avg Travel Distance: ${category.avgTravelDistance.toFixed(1)}km`);
    print(`  Max Travel Distance: ${category.maxTravelDistance.toFixed(1)}km`);
    print(`  Avg Preferred Radius: ${category.avgPreferredRadius.toFixed(1)}km`);
    print(`  Travel vs Preference Ratio: ${category.travelVsPreference.toFixed(2)}`);
    print(`  Sample Size: ${category.attendeeCount} attendees`);
});

print("\nGeospatial Aggregation Pipelines completed successfully!");
print("=".repeat(60));
