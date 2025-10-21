// Basic CRUD Operations for Users, Reviews, and Checkins Collections
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("=".repeat(60));
print("USERS, REVIEWS & CHECKINS - CRUD OPERATIONS");
print("=".repeat(60));

// ===== USERS COLLECTION CRUD =====
print("\n1. USERS COLLECTION - CRUD OPERATIONS");
print("-".repeat(40));

// CREATE - Add new users
print("Creating new users...");
db.users.insertMany([
    {
        email: "alex.thompson@gmail.com",
        schemaVersion: "1.0",
        profile: {
            firstName: "Alex",
            lastName: "Thompson",
            preferences: {
                categories: ["Technology", "Business", "Networking"],
                location: {
                    type: "Point",
                    coordinates: [-123.1207, 49.2827] // Vancouver
                },
                radiusKm: 30
            }
        },
        createdAt: new Date(),
        updatedAt: new Date(),
        lastLogin: new Date()
    },
    {
        email: "maria.garcia@outlook.com",
        schemaVersion: "1.0",
        profile: {
            firstName: "Maria",
            lastName: "Garcia",
            preferences: {
                categories: ["Arts & Culture", "Music", "Food & Drink"],
                location: {
                    type: "Point",
                    coordinates: [-123.9351, 49.0831] // Nanaimo
                },
                radiusKm: 50
            }
        },
        createdAt: new Date(),
        updatedAt: new Date(),
        lastLogin: null
    }
]);

// READ - Find users
print("\nFinding users by preferences:");
db.users.find({ "profile.preferences.categories": "Technology" }).forEach(user => {
    print(`- ${user.profile.firstName} ${user.profile.lastName} (${user.email})`);
});

print("\nFinding users in Vancouver area:");
db.users.find({
    "profile.preferences.location.coordinates.0": { $gte: -123.3, $lte: -123.0 },
    "profile.preferences.location.coordinates.1": { $gte: 49.2, $lte: 49.3 }
}).forEach(user => {
    print(`- ${user.profile.firstName} ${user.profile.lastName} - Radius: ${user.profile.preferences.radiusKm}km`);
});

// UPDATE - Update user preferences
print("\nUpdating user preferences...");
db.users.updateOne(
    { email: "alex.thompson@gmail.com" },
    {
        $addToSet: { "profile.preferences.categories": "Health & Wellness" },
        $set: { 
            lastLogin: new Date(),
            updatedAt: new Date()
        }
    }
);

// UPDATE - Update user location
print("Updating user location...");
db.users.updateOne(
    { email: "maria.garcia@outlook.com" },
    {
        $set: {
            "profile.preferences.location": {
                type: "Point",
                coordinates: [-123.1207, 49.2827] // Moved to Vancouver
            },
            "profile.preferences.radiusKm": 25,
            updatedAt: new Date()
        }
    }
);

// ===== REVIEWS COLLECTION CRUD =====
print("\n2. REVIEWS COLLECTION - CRUD OPERATIONS");
print("-".repeat(40));

// First, get some event and user IDs for reviews
const sampleEvent = db.events.findOne({ title: { $regex: /Tech/ } });
const sampleVenue = db.venues.findOne({ venueType: "conferenceCenter" });
const sampleUser = db.users.findOne({ email: "alex.thompson@gmail.com" });

if (sampleEvent && sampleUser) {
    // CREATE - Add event reviews
    print("Creating event reviews...");
    db.reviews.insertMany([
        {
            eventId: sampleEvent._id,
            userId: sampleUser._id,
            rating: 5,
            comment: "Excellent tech summit! Great speakers and valuable networking opportunities. The hybrid format worked seamlessly.",
            schemaVersion: "1.0",
            createdAt: new Date(),
            updatedAt: null
        },
        {
            eventId: sampleEvent._id,
            userId: ObjectId(), // Different user
            rating: 4,
            comment: "Good content and organization. The virtual component could use some improvement, but overall worth attending.",
            schemaVersion: "1.0",
            createdAt: new Date(),
            updatedAt: null
        }
    ]);
}

if (sampleVenue && sampleUser) {
    // CREATE - Add venue review
    print("Creating venue review...");
    db.reviews.insertOne({
        venueId: sampleVenue._id,
        userId: sampleUser._id,
        rating: 4,
        comment: "Professional venue with excellent facilities. Great location and helpful staff. Parking could be better.",
        schemaVersion: "1.0",
        createdAt: new Date(),
        updatedAt: null
    });
}

// READ - Find reviews by rating
print("\nFinding 5-star reviews:");
db.reviews.find({ rating: 5 }).forEach(review => {
    const type = review.eventId ? "Event" : "Venue";
    print(`- ${type} Review: ${review.rating} stars - "${review.comment.substring(0, 50)}..."`);
});

// READ - Find reviews by user
if (sampleUser) {
    print(`\nFinding reviews by ${sampleUser.profile.firstName}:`);
    db.reviews.find({ userId: sampleUser._id }).forEach(review => {
        const type = review.eventId ? "Event" : "Venue";
        print(`- ${type} Review: ${review.rating} stars - ${review.createdAt.toISOString().split('T')[0]}`);
    });
}

// UPDATE - Update review
print("\nUpdating a review...");
db.reviews.updateOne(
    { rating: 4, comment: { $regex: /Good content/ } },
    {
        $set: {
            comment: "Good content and organization. The virtual component has improved since my last feedback. Recommended!",
            updatedAt: new Date()
        }
    }
);

// READ - Aggregate reviews by rating
print("\nReview rating distribution:");
db.reviews.aggregate([
    { $group: { _id: "$rating", count: { $sum: 1 } } },
    { $sort: { _id: 1 } }
]).forEach(result => {
    print(`- ${result._id} stars: ${result.count} reviews`);
});

// ===== CHECKINS COLLECTION CRUD =====
print("\n3. CHECKINS COLLECTION - CRUD OPERATIONS");
print("-".repeat(40));

// Get sample data for checkins
const sampleEvent2 = db.events.findOne({ eventType: "hybrid" });
const sampleVenue2 = db.venues.findOne({ venueType: "park" });
const sampleUser2 = db.users.findOne({ email: "maria.garcia@outlook.com" });

if (sampleEvent2 && sampleVenue2 && sampleUser2) {
    // CREATE - Add checkins
    print("Creating check-ins...");
    db.checkins.insertMany([
        {
            eventId: sampleEvent2._id,
            userId: sampleUser2._id,
            venueId: sampleVenue2._id,
            checkInTime: new Date("2025-10-09T18:30:00Z"),
            qrCode: "QR-HYBRID-001",
            schemaVersion: "1.0",
            ticketTier: "General Admission",
            checkInMethod: "qrCode",
            location: {
                type: "Point",
                coordinates: [-123.1139, 49.2404]
            },
            metadata: {
                deviceInfo: "iPhone 15",
                ipAddress: "192.168.1.105",
                staffVerified: true
            },
            createdAt: new Date(),
            updatedAt: new Date()
        },
        {
            eventId: sampleEvent2._id,
            userId: sampleUser._id,
            venueId: sampleVenue2._id,
            checkInTime: new Date("2025-10-09T18:45:00Z"),
            qrCode: "QR-HYBRID-002",
            schemaVersion: "1.0",
            ticketTier: "Early Bird",
            checkInMethod: "mobileApp",
            location: {
                type: "Point",
                coordinates: [-123.1139, 49.2404]
            },
            metadata: {
                deviceInfo: "Android Samsung S24",
                ipAddress: "192.168.1.106",
                staffVerified: false
            },
            createdAt: new Date(),
            updatedAt: new Date()
        }
    ]);
}

// READ - Find checkins by event
if (sampleEvent2) {
    print(`\nFinding check-ins for event:`);
    db.checkins.find({ eventId: sampleEvent2._id }).forEach(checkin => {
        print(`- User checked in at ${checkin.checkInTime.toISOString()} via ${checkin.checkInMethod}`);
    });
}

// READ - Find checkins by method
print("\nFinding QR code check-ins:");
db.checkins.find({ checkInMethod: "qrCode" }).forEach(checkin => {
    print(`- QR Code: ${checkin.qrCode} - ${checkin.checkInTime.toISOString()}`);
});

// READ - Find checkins by user
if (sampleUser) {
    print(`\nFinding check-ins by user:`);
    db.checkins.find({ userId: sampleUser._id }).forEach(checkin => {
        print(`- Checked in: ${checkin.checkInTime.toISOString()} - Tier: ${checkin.ticketTier}`);
    });
}

// UPDATE - Update checkin metadata
print("\nUpdating check-in verification status...");
db.checkins.updateMany(
    { checkInMethod: "mobileApp" },
    {
        $set: {
            "metadata.staffVerified": true,
            "metadata.verificationTime": new Date(),
            updatedAt: new Date()
        }
    }
);

// READ - Aggregate checkins by method
print("\nCheck-in method distribution:");
db.checkins.aggregate([
    { $group: { _id: "$checkInMethod", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
]).forEach(result => {
    print(`- ${result._id}: ${result.count} check-ins`);
});

// ===== CROSS-COLLECTION OPERATIONS =====
print("\n4. CROSS-COLLECTION OPERATIONS");
print("-".repeat(40));

// Find users who have reviewed events
print("Finding users who have written reviews:");
db.reviews.aggregate([
    { $group: { _id: "$userId", reviewCount: { $sum: 1 } } },
    { $lookup: { 
        from: "users", 
        localField: "_id", 
        foreignField: "_id", 
        as: "user" 
    }},
    { $unwind: "$user" },
    { $project: {
        name: { $concat: ["$user.profile.firstName", " ", "$user.profile.lastName"] },
        email: "$user.email",
        reviewCount: 1
    }}
]).forEach(result => {
    print(`- ${result.name} (${result.email}): ${result.reviewCount} reviews`);
});

// Find events with their check-in counts
print("\nFinding events with check-in statistics:");
db.checkins.aggregate([
    { $group: { 
        _id: "$eventId", 
        totalCheckins: { $sum: 1 },
        uniqueMethods: { $addToSet: "$checkInMethod" }
    }},
    { $lookup: { 
        from: "events", 
        localField: "_id", 
        foreignField: "_id", 
        as: "event" 
    }},
    { $unwind: "$event" },
    { $project: {
        eventTitle: "$event.title",
        totalCheckins: 1,
        methodCount: { $size: "$uniqueMethods" }
    }}
]).forEach(result => {
    print(`- ${result.eventTitle}: ${result.totalCheckins} check-ins using ${result.methodCount} methods`);
});

// ===== DELETE OPERATIONS =====
print("\n5. DELETE OPERATIONS");
print("-".repeat(40));

// Delete old reviews (older than 2 years)
const twoYearsAgo = new Date();
twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2);

print("Deleting old reviews...");
const oldReviewsResult = db.reviews.deleteMany({
    createdAt: { $lt: twoYearsAgo }
});
print(`Deleted ${oldReviewsResult.deletedCount} old reviews`);

// Delete checkins for cancelled events
print("Deleting check-ins for cancelled events...");
const cancelledEvents = db.events.find({ status: "cancelled" }, { _id: 1 }).toArray();
const cancelledEventIds = cancelledEvents.map(event => event._id);

if (cancelledEventIds.length > 0) {
    const cancelledCheckinsResult = db.checkins.deleteMany({
        eventId: { $in: cancelledEventIds }
    });
    print(`Deleted ${cancelledCheckinsResult.deletedCount} check-ins for cancelled events`);
}

// Delete inactive users (no login in last year and no reviews/checkins)
const oneYearAgo = new Date();
oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

print("Finding inactive users for cleanup...");
const activeUserIds = [
    ...db.reviews.distinct("userId"),
    ...db.checkins.distinct("userId")
];

const inactiveUsersResult = db.users.deleteMany({
    $and: [
        { 
            $or: [
                { lastLogin: { $lt: oneYearAgo } },
                { lastLogin: null }
            ]
        },
        { _id: { $nin: activeUserIds } },
        { email: { $regex: /test|demo/i } } // Only delete test users
    ]
});
print(`Deleted ${inactiveUsersResult.deletedCount} inactive test users`);

// ===== ADVANCED OPERATIONS =====
print("\n6. ADVANCED OPERATIONS");
print("-".repeat(40));

// Bulk operations across collections
print("Performing bulk operations...");

// Update user activity based on recent checkins
const recentCheckins = db.checkins.aggregate([
    { $match: { checkInTime: { $gte: new Date(Date.now() - 30*24*60*60*1000) } } }, // Last 30 days
    { $group: { _id: "$userId", recentActivity: { $sum: 1 } } }
]).toArray();

recentCheckins.forEach(activity => {
    db.users.updateOne(
        { _id: activity._id },
        { 
            $set: { 
                "profile.activityLevel": activity.recentActivity > 5 ? "high" : "moderate",
                updatedAt: new Date()
            }
        }
    );
});

// Create user engagement summary
print("Creating user engagement summary:");
db.users.aggregate([
    { $lookup: { 
        from: "reviews", 
        localField: "_id", 
        foreignField: "userId", 
        as: "reviews" 
    }},
    { $lookup: { 
        from: "checkins", 
        localField: "_id", 
        foreignField: "userId", 
        as: "checkins" 
    }},
    { $project: {
        name: { $concat: ["$profile.firstName", " ", "$profile.lastName"] },
        email: 1,
        reviewCount: { $size: "$reviews" },
        checkinCount: { $size: "$checkins" },
        engagementScore: { $add: [{ $size: "$reviews" }, { $size: "$checkins" }] }
    }},
    { $sort: { engagementScore: -1 } }
]).forEach(user => {
    print(`- ${user.name}: ${user.reviewCount} reviews, ${user.checkinCount} check-ins (Score: ${user.engagementScore})`);
});

print("\nUsers, Reviews & Checkins CRUD Operations completed successfully!");
print("=".repeat(60));
