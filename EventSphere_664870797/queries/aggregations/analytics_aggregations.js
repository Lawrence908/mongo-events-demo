// Analytics Aggregation Pipelines for EventSphere
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("=".repeat(60));
print("ANALYTICS AGGREGATION PIPELINES");
print("=".repeat(60));

// ===== 1. EVENT PERFORMANCE ANALYTICS =====
print("\n1. EVENT PERFORMANCE ANALYTICS");
print("-".repeat(40));

// Comprehensive event performance metrics
print("Analyzing event performance metrics:");
db.events.aggregate([
    {
        $match: {
            status: { $in: ["published", "completed"] },
            startDate: { $gte: new Date("2025-01-01") }
        }
    },
    {
        $lookup: {
            from: "reviews",
            localField: "_id",
            foreignField: "eventId",
            as: "reviews"
        }
    },
    {
        $lookup: {
            from: "checkins",
            localField: "_id",
            foreignField: "eventId",
            as: "checkins"
        }
    },
    {
        $addFields: {
            actualAttendees: { $size: "$checkins" },
            reviewCount: { $size: "$reviews" },
            avgRating: { $avg: "$reviews.rating" },
            attendanceRate: {
                $cond: [
                    { $gt: ["$maxAttendees", 0] },
                    { $multiply: [{ $divide: [{ $size: "$checkins" }, "$maxAttendees"] }, 100] },
                    0
                ]
            },
            revenuePerAttendee: {
                $cond: [
                    { $gt: [{ $size: "$checkins" }, 0] },
                    { $divide: ["$computedStats.totalRevenue", { $size: "$checkins" }] },
                    0
                ]
            }
        }
    },
    {
        $group: {
            _id: "$category",
            eventCount: { $sum: 1 },
            avgAttendance: { $avg: "$actualAttendees" },
            avgAttendanceRate: { $avg: "$attendanceRate" },
            avgRating: { $avg: "$avgRating" },
            totalRevenue: { $sum: "$computedStats.totalRevenue" },
            avgRevenuePerEvent: { $avg: "$computedStats.totalRevenue" },
            avgRevenuePerAttendee: { $avg: "$revenuePerAttendee" },
            topEvent: { 
                $first: {
                    $sortArray: {
                        input: "$$ROOT",
                        sortBy: { attendanceRate: -1 }
                    }
                }
            }
        }
    },
    {
        $sort: { totalRevenue: -1 }
    }
]).forEach(category => {
    print(`${category._id}:`);
    print(`  Events: ${category.eventCount}`);
    print(`  Avg Attendance: ${category.avgAttendance.toFixed(1)} people`);
    print(`  Avg Attendance Rate: ${category.avgAttendanceRate.toFixed(1)}%`);
    print(`  Avg Rating: ${category.avgRating ? category.avgRating.toFixed(2) : 'N/A'}/5`);
    print(`  Total Revenue: $${category.totalRevenue.toFixed(2)} CAD`);
    print(`  Avg Revenue/Event: $${category.avgRevenuePerEvent.toFixed(2)} CAD`);
    print(`  Avg Revenue/Attendee: $${category.avgRevenuePerAttendee.toFixed(2)} CAD`);
});

// ===== 2. TEMPORAL ANALYTICS =====
print("\n2. TEMPORAL ANALYTICS");
print("-".repeat(40));

// Event timing patterns and trends
print("Analyzing event timing patterns:");
db.events.aggregate([
    {
        $match: {
            startDate: { $gte: new Date("2025-01-01") }
        }
    },
    {
        $addFields: {
            dayOfWeek: { $dayOfWeek: "$startDate" },
            hour: { $hour: "$startDate" },
            month: { $month: "$startDate" },
            dayName: {
                $switch: {
                    branches: [
                        { case: { $eq: ["$dayOfWeek", 1] }, then: "Sunday" },
                        { case: { $eq: ["$dayOfWeek", 2] }, then: "Monday" },
                        { case: { $eq: ["$dayOfWeek", 3] }, then: "Tuesday" },
                        { case: { $eq: ["$dayOfWeek", 4] }, then: "Wednesday" },
                        { case: { $eq: ["$dayOfWeek", 5] }, then: "Thursday" },
                        { case: { $eq: ["$dayOfWeek", 6] }, then: "Friday" },
                        { case: { $eq: ["$dayOfWeek", 7] }, then: "Saturday" }
                    ]
                }
            },
            timeSlot: {
                $switch: {
                    branches: [
                        { case: { $lt: ["$hour", 6] }, then: "Late Night (0-6)" },
                        { case: { $lt: ["$hour", 12] }, then: "Morning (6-12)" },
                        { case: { $lt: ["$hour", 17] }, then: "Afternoon (12-17)" },
                        { case: { $lt: ["$hour", 21] }, then: "Evening (17-21)" }
                    ],
                    default: "Night (21-24)"
                }
            }
        }
    },
    {
        $group: {
            _id: {
                dayName: "$dayName",
                timeSlot: "$timeSlot"
            },
            eventCount: { $sum: 1 },
            avgPrice: { $avg: "$price" },
            categories: { $addToSet: "$category" },
            eventTypes: { $addToSet: "$eventType" }
        }
    },
    {
        $sort: { eventCount: -1 }
    },
    {
        $limit: 10
    }
]).forEach(timePattern => {
    print(`${timePattern._id.dayName} ${timePattern._id.timeSlot}:`);
    print(`  Events: ${timePattern.eventCount}`);
    print(`  Avg Price: $${timePattern.avgPrice.toFixed(2)} CAD`);
    print(`  Categories: ${timePattern.categories.join(', ')}`);
    print(`  Types: ${timePattern.eventTypes.join(', ')}`);
});

// Monthly event trends
print("\nMonthly event creation trends:");
db.events.aggregate([
    {
        $group: {
            _id: {
                year: { $year: "$createdAt" },
                month: { $month: "$createdAt" }
            },
            eventsCreated: { $sum: 1 },
            avgPrice: { $avg: "$price" },
            freeEvents: { $sum: { $cond: [{ $eq: ["$isFree", true] }, 1, 0] } },
            categories: { $addToSet: "$category" }
        }
    },
    {
        $addFields: {
            freeEventPercentage: { 
                $multiply: [{ $divide: ["$freeEvents", "$eventsCreated"] }, 100] 
            }
        }
    },
    {
        $sort: { "_id.year": 1, "_id.month": 1 }
    }
]).forEach(month => {
    print(`${month._id.year}-${month._id.month.toString().padStart(2, '0')}:`);
    print(`  Events Created: ${month.eventsCreated}`);
    print(`  Avg Price: $${month.avgPrice.toFixed(2)} CAD`);
    print(`  Free Events: ${month.freeEventPercentage.toFixed(1)}%`);
    print(`  Categories: ${month.categories.length} different`);
});

// ===== 3. VENUE UTILIZATION ANALYTICS =====
print("\n3. VENUE UTILIZATION ANALYTICS");
print("-".repeat(40));

// Comprehensive venue performance analysis
print("Analyzing venue utilization and performance:");
db.venues.aggregate([
    {
        $lookup: {
            from: "events",
            localField: "_id",
            foreignField: "venueId",
            as: "hostedEvents"
        }
    },
    {
        $lookup: {
            from: "checkins",
            localField: "_id",
            foreignField: "venueId",
            as: "checkins"
        }
    },
    {
        $lookup: {
            from: "reviews",
            localField: "_id",
            foreignField: "venueId",
            as: "venueReviews"
        }
    },
    {
        $addFields: {
            totalEvents: { $size: "$hostedEvents" },
            totalAttendees: { $size: "$checkins" },
            avgAttendeesPerEvent: {
                $cond: [
                    { $gt: [{ $size: "$hostedEvents" }, 0] },
                    { $divide: [{ $size: "$checkins" }, { $size: "$hostedEvents" }] },
                    0
                ]
            },
            capacityUtilization: {
                $cond: [
                    { $and: [{ $gt: ["$capacity", 0] }, { $gt: [{ $size: "$hostedEvents" }, 0] }] },
                    { $multiply: [
                        { $divide: [
                            { $divide: [{ $size: "$checkins" }, { $size: "$hostedEvents" }] },
                            "$capacity"
                        ]}, 
                        100
                    ]},
                    0
                ]
            },
            venueRating: { $avg: "$venueReviews.rating" },
            revenueGenerated: { $sum: "$hostedEvents.computedStats.totalRevenue" }
        }
    },
    {
        $match: { totalEvents: { $gt: 0 } }
    },
    {
        $group: {
            _id: "$venueType",
            venueCount: { $sum: 1 },
            avgEventsPerVenue: { $avg: "$totalEvents" },
            avgCapacityUtilization: { $avg: "$capacityUtilization" },
            avgVenueRating: { $avg: "$venueRating" },
            totalRevenue: { $sum: "$revenueGenerated" },
            topVenue: {
                $first: {
                    $sortArray: {
                        input: "$$ROOT",
                        sortBy: { totalEvents: -1 }
                    }
                }
            }
        }
    },
    {
        $sort: { totalRevenue: -1 }
    }
]).forEach(venueType => {
    print(`${venueType._id}:`);
    print(`  Venues: ${venueType.venueCount}`);
    print(`  Avg Events/Venue: ${venueType.avgEventsPerVenue.toFixed(1)}`);
    print(`  Avg Capacity Utilization: ${venueType.avgCapacityUtilization.toFixed(1)}%`);
    print(`  Avg Rating: ${venueType.avgVenueRating ? venueType.avgVenueRating.toFixed(2) : 'N/A'}/5`);
    print(`  Total Revenue: $${venueType.totalRevenue.toFixed(2)} CAD`);
    if (venueType.topVenue) {
        print(`  Top Venue: ${venueType.topVenue.name} (${venueType.topVenue.totalEvents} events)`);
    }
});

// ===== 4. USER ENGAGEMENT ANALYTICS =====
print("\n4. USER ENGAGEMENT ANALYTICS");
print("-".repeat(40));

// User behavior and engagement patterns
print("Analyzing user engagement patterns:");
db.users.aggregate([
    {
        $lookup: {
            from: "checkins",
            localField: "_id",
            foreignField: "userId",
            as: "checkins"
        }
    },
    {
        $lookup: {
            from: "reviews",
            localField: "_id",
            foreignField: "userId",
            as: "reviews"
        }
    },
    {
        $addFields: {
            totalCheckins: { $size: "$checkins" },
            totalReviews: { $size: "$reviews" },
            avgReviewRating: { $avg: "$reviews.rating" },
            engagementScore: { $add: [{ $size: "$checkins" }, { $multiply: [{ $size: "$reviews" }, 2] }] },
            userType: {
                $switch: {
                    branches: [
                        { case: { $eq: [{ $size: "$checkins" }, 0] }, then: "Inactive" },
                        { case: { $lte: [{ $size: "$checkins" }, 2] }, then: "Casual" },
                        { case: { $lte: [{ $size: "$checkins" }, 5] }, then: "Regular" },
                        { case: { $lte: [{ $size: "$checkins" }, 10] }, then: "Active" }
                    ],
                    default: "Super User"
                }
            }
        }
    },
    {
        $group: {
            _id: "$userType",
            userCount: { $sum: 1 },
            avgCheckins: { $avg: "$totalCheckins" },
            avgReviews: { $avg: "$totalReviews" },
            avgEngagementScore: { $avg: "$engagementScore" },
            avgReviewRating: { $avg: "$avgReviewRating" },
            totalCheckins: { $sum: "$totalCheckins" },
            totalReviews: { $sum: "$totalReviews" }
        }
    },
    {
        $sort: { avgEngagementScore: -1 }
    }
]).forEach(userType => {
    print(`${userType._id} Users:`);
    print(`  Count: ${userType.userCount}`);
    print(`  Avg Check-ins: ${userType.avgCheckins.toFixed(1)}`);
    print(`  Avg Reviews: ${userType.avgReviews.toFixed(1)}`);
    print(`  Avg Engagement Score: ${userType.avgEngagementScore.toFixed(1)}`);
    print(`  Avg Review Rating: ${userType.avgReviewRating ? userType.avgReviewRating.toFixed(2) : 'N/A'}/5`);
    print(`  Total Activity: ${userType.totalCheckins} check-ins, ${userType.totalReviews} reviews`);
});

// ===== 5. REVENUE ANALYTICS =====
print("\n5. REVENUE ANALYTICS");
print("-".repeat(40));

// Revenue analysis by various dimensions
print("Analyzing revenue patterns:");
db.events.aggregate([
    {
        $match: {
            "computedStats.totalRevenue": { $gt: 0 }
        }
    },
    {
        $group: {
            _id: {
                category: "$category",
                eventType: "$eventType"
            },
            eventCount: { $sum: 1 },
            totalRevenue: { $sum: "$computedStats.totalRevenue" },
            avgRevenue: { $avg: "$computedStats.totalRevenue" },
            avgPrice: { $avg: "$price" },
            avgTicketsSold: { $avg: "$computedStats.totalTicketsSold" },
            maxRevenue: { $max: "$computedStats.totalRevenue" },
            minRevenue: { $min: "$computedStats.totalRevenue" }
        }
    },
    {
        $addFields: {
            revenuePerTicket: { $divide: ["$totalRevenue", "$avgTicketsSold"] }
        }
    },
    {
        $sort: { totalRevenue: -1 }
    },
    {
        $limit: 10
    }
]).forEach(segment => {
    print(`${segment._id.category} (${segment._id.eventType}):`);
    print(`  Events: ${segment.eventCount}`);
    print(`  Total Revenue: $${segment.totalRevenue.toFixed(2)} CAD`);
    print(`  Avg Revenue/Event: $${segment.avgRevenue.toFixed(2)} CAD`);
    print(`  Avg Ticket Price: $${segment.avgPrice.toFixed(2)} CAD`);
    print(`  Avg Tickets Sold: ${segment.avgTicketsSold.toFixed(1)}`);
    print(`  Revenue Range: $${segment.minRevenue.toFixed(2)} - $${segment.maxRevenue.toFixed(2)} CAD`);
});

// ===== 6. POLYMORPHIC EVENT TYPE ANALYSIS =====
print("\n6. POLYMORPHIC EVENT TYPE ANALYSIS");
print("-".repeat(40));

// Advanced analysis of different event types
print("Analyzing polymorphic event type performance:");
db.events.aggregate([
    {
        $facet: {
            virtualEvents: [
                { $match: { eventType: "virtual" } },
                {
                    $group: {
                        _id: "$virtualDetails.platform",
                        count: { $sum: 1 },
                        avgAttendance: { $avg: "$currentAttendees" },
                        recordingAvailable: { $sum: { $cond: ["$virtualDetails.recordingAvailable", 1, 0] } }
                    }
                }
            ],
            hybridEvents: [
                { $match: { eventType: "hybrid" } },
                {
                    $group: {
                        _id: null,
                        count: { $sum: 1 },
                        avgVirtualCapacity: { $avg: "$hybridDetails.virtualCapacity" },
                        avgInPersonCapacity: { $avg: "$hybridDetails.inPersonCapacity" },
                        totalCapacity: { $sum: { $add: ["$hybridDetails.virtualCapacity", "$hybridDetails.inPersonCapacity"] } }
                    }
                }
            ],
            recurringEvents: [
                { $match: { eventType: "recurring" } },
                {
                    $group: {
                        _id: "$recurringDetails.frequency",
                        count: { $sum: 1 },
                        avgDuration: { $avg: { $divide: [{ $subtract: ["$recurringDetails.endRecurrence", "$startDate"] }, 86400000] } }
                    }
                }
            ],
            inPersonEvents: [
                { $match: { eventType: "inPerson" } },
                {
                    $group: {
                        _id: null,
                        count: { $sum: 1 },
                        avgCapacity: { $avg: "$maxAttendees" },
                        withVenues: { $sum: { $cond: [{ $ne: ["$venueId", null] }, 1, 0] } }
                    }
                }
            ]
        }
    }
]).forEach(analysis => {
    print("Virtual Events by Platform:");
    analysis.virtualEvents.forEach(platform => {
        print(`  ${platform._id || 'Unknown'}: ${platform.count} events, avg ${platform.avgAttendance.toFixed(1)} attendees`);
        print(`    Recording Available: ${platform.recordingAvailable}/${platform.count}`);
    });
    
    print("\nHybrid Events Analysis:");
    analysis.hybridEvents.forEach(hybrid => {
        print(`  Total Hybrid Events: ${hybrid.count}`);
        print(`  Avg Virtual Capacity: ${hybrid.avgVirtualCapacity.toFixed(0)}`);
        print(`  Avg In-Person Capacity: ${hybrid.avgInPersonCapacity.toFixed(0)}`);
        print(`  Total Combined Capacity: ${hybrid.totalCapacity}`);
    });
    
    print("\nRecurring Events by Frequency:");
    analysis.recurringEvents.forEach(recurring => {
        print(`  ${recurring._id}: ${recurring.count} events, avg ${recurring.avgDuration.toFixed(0)} days duration`);
    });
    
    print("\nIn-Person Events Analysis:");
    analysis.inPersonEvents.forEach(inPerson => {
        print(`  Total In-Person Events: ${inPerson.count}`);
        print(`  Avg Capacity: ${inPerson.avgCapacity.toFixed(0)}`);
        print(`  With Venues: ${inPerson.withVenues}/${inPerson.count} (${(inPerson.withVenues/inPerson.count*100).toFixed(1)}%)`);
    });
});

print("\nAnalytics Aggregation Pipelines completed successfully!");
print("=".repeat(60));
