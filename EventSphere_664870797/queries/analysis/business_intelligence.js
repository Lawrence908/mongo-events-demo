// Business Intelligence Analysis Queries for EventSphere
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("=".repeat(60));
print("BUSINESS INTELLIGENCE ANALYSIS");
print("=".repeat(60));

// ===== 1. REVENUE ANALYSIS =====
print("\n1. REVENUE ANALYSIS");
print("-".repeat(40));

// Comprehensive revenue analysis across multiple dimensions
print("Analyzing revenue patterns and trends:");

db.events.aggregate([
    {
        $match: {
            "computedStats.totalRevenue": { $gt: 0 },
            status: { $in: ["published", "completed"] }
        }
    },
    {
        $addFields: {
            revenueCategory: {
                $switch: {
                    branches: [
                        { case: { $lt: ["$computedStats.totalRevenue", 1000] }, then: "Low ($0-$999)" },
                        { case: { $lt: ["$computedStats.totalRevenue", 5000] }, then: "Medium ($1K-$4.9K)" },
                        { case: { $lt: ["$computedStats.totalRevenue", 15000] }, then: "High ($5K-$14.9K)" }
                    ],
                    default: "Premium ($15K+)"
                }
            },
            monthYear: {
                $dateToString: { format: "%Y-%m", date: "$startDate" }
            },
            quarter: {
                $concat: [
                    { $toString: { $year: "$startDate" } },
                    "-Q",
                    { $toString: { $ceil: { $divide: [{ $month: "$startDate" }, 3] } } }
                ]
            }
        }
    },
    {
        $facet: {
            byCategory: [
                {
                    $group: {
                        _id: "$category",
                        totalRevenue: { $sum: "$computedStats.totalRevenue" },
                        eventCount: { $sum: 1 },
                        avgRevenue: { $avg: "$computedStats.totalRevenue" },
                        avgTicketPrice: { $avg: "$price" },
                        avgTicketsSold: { $avg: "$computedStats.totalTicketsSold" },
                        maxRevenue: { $max: "$computedStats.totalRevenue" },
                        minRevenue: { $min: "$computedStats.totalRevenue" }
                    }
                },
                { $sort: { totalRevenue: -1 } }
            ],
            byEventType: [
                {
                    $group: {
                        _id: "$eventType",
                        totalRevenue: { $sum: "$computedStats.totalRevenue" },
                        eventCount: { $sum: 1 },
                        avgRevenue: { $avg: "$computedStats.totalRevenue" },
                        avgAttendanceRate: { $avg: "$computedStats.attendanceRate" }
                    }
                },
                { $sort: { totalRevenue: -1 } }
            ],
            byRevenueCategory: [
                {
                    $group: {
                        _id: "$revenueCategory",
                        eventCount: { $sum: 1 },
                        totalRevenue: { $sum: "$computedStats.totalRevenue" },
                        categories: { $addToSet: "$category" }
                    }
                },
                { $sort: { totalRevenue: -1 } }
            ],
            byQuarter: [
                {
                    $group: {
                        _id: "$quarter",
                        totalRevenue: { $sum: "$computedStats.totalRevenue" },
                        eventCount: { $sum: 1 },
                        avgRevenue: { $avg: "$computedStats.totalRevenue" }
                    }
                },
                { $sort: { _id: 1 } }
            ]
        }
    }
]).forEach(analysis => {
    print("REVENUE BY CATEGORY:");
    analysis.byCategory.forEach(cat => {
        print(`${cat._id}:`);
        print(`  Total Revenue: $${cat.totalRevenue.toFixed(2)} CAD`);
        print(`  Events: ${cat.eventCount}`);
        print(`  Avg Revenue/Event: $${cat.avgRevenue.toFixed(2)} CAD`);
        print(`  Avg Ticket Price: $${cat.avgTicketPrice.toFixed(2)} CAD`);
        print(`  Avg Tickets Sold: ${cat.avgTicketsSold.toFixed(0)}`);
        print(`  Revenue Range: $${cat.minRevenue.toFixed(2)} - $${cat.maxRevenue.toFixed(2)} CAD`);
    });
    
    print("\nREVENUE BY EVENT TYPE:");
    analysis.byEventType.forEach(type => {
        print(`${type._id}:`);
        print(`  Total Revenue: $${type.totalRevenue.toFixed(2)} CAD`);
        print(`  Events: ${type.eventCount}`);
        print(`  Avg Revenue/Event: $${type.avgRevenue.toFixed(2)} CAD`);
        print(`  Avg Attendance Rate: ${type.avgAttendanceRate.toFixed(1)}%`);
    });
    
    print("\nREVENUE DISTRIBUTION:");
    analysis.byRevenueCategory.forEach(range => {
        print(`${range._id}:`);
        print(`  Events: ${range.eventCount}`);
        print(`  Total Revenue: $${range.totalRevenue.toFixed(2)} CAD`);
        print(`  Categories: ${range.categories.join(', ')}`);
    });
    
    print("\nQUARTERLY REVENUE TRENDS:");
    analysis.byQuarter.forEach(quarter => {
        print(`${quarter._id}:`);
        print(`  Revenue: $${quarter.totalRevenue.toFixed(2)} CAD`);
        print(`  Events: ${quarter.eventCount}`);
        print(`  Avg/Event: $${quarter.avgRevenue.toFixed(2)} CAD`);
    });
});

// ===== 2. CUSTOMER SEGMENTATION =====
print("\n2. CUSTOMER SEGMENTATION");
print("-".repeat(40));

// Advanced user segmentation based on behavior
print("Analyzing customer segments and behavior:");

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
            daysSinceLastLogin: {
                $divide: [
                    { $subtract: [new Date(), { $ifNull: ["$lastLogin", "$createdAt"] }] },
                    86400000
                ]
            },
            accountAge: {
                $divide: [
                    { $subtract: [new Date(), "$createdAt"] },
                    86400000
                ]
            }
        }
    },
    {
        $addFields: {
            engagementLevel: {
                $switch: {
                    branches: [
                        { case: { $eq: ["$totalCheckins", 0] }, then: "Inactive" },
                        { case: { $lte: ["$totalCheckins", 2] }, then: "New/Casual" },
                        { case: { $lte: ["$totalCheckins", 5] }, then: "Regular" },
                        { case: { $lte: ["$totalCheckins", 10] }, then: "Active" }
                    ],
                    default: "Power User"
                }
            },
            reviewerType: {
                $switch: {
                    branches: [
                        { case: { $eq: ["$totalReviews", 0] }, then: "Non-Reviewer" },
                        { case: { $lte: ["$totalReviews", 2] }, then: "Occasional Reviewer" },
                        { case: { $lte: ["$totalReviews", 5] }, then: "Regular Reviewer" }
                    ],
                    default: "Prolific Reviewer"
                }
            },
            loyaltySegment: {
                $switch: {
                    branches: [
                        { case: { $and: [{ $gte: ["$accountAge", 365] }, { $gte: ["$totalCheckins", 5] }] }, then: "Loyal Customer" },
                        { case: { $and: [{ $gte: ["$accountAge", 180] }, { $gte: ["$totalCheckins", 3] }] }, then: "Growing Customer" },
                        { case: { $and: [{ $lte: ["$accountAge", 90] }, { $gte: ["$totalCheckins", 2] }] }, then: "Fast Adopter" },
                        { case: { $gte: ["$daysSinceLastLogin", 90] }, then: "At Risk" }
                    ],
                    default: "Standard Customer"
                }
            }
        }
    },
    {
        $group: {
            _id: {
                engagement: "$engagementLevel",
                reviewer: "$reviewerType",
                loyalty: "$loyaltySegment"
            },
            userCount: { $sum: 1 },
            avgCheckins: { $avg: "$totalCheckins" },
            avgReviews: { $avg: "$totalReviews" },
            avgReviewRating: { $avg: "$avgReviewRating" },
            avgAccountAge: { $avg: "$accountAge" },
            avgDaysSinceLogin: { $avg: "$daysSinceLastLogin" },
            preferredCategories: { $push: "$profile.preferences.categories" }
        }
    },
    {
        $addFields: {
            topCategories: {
                $slice: [
                    {
                        $setIntersection: [
                            { $reduce: {
                                input: "$preferredCategories",
                                initialValue: [],
                                in: { $concatArrays: ["$$value", { $ifNull: ["$$this", []] }] }
                            }}
                        ]
                    },
                    3
                ]
            }
        }
    },
    {
        $sort: { userCount: -1 }
    },
    {
        $limit: 15
    }
]).forEach(segment => {
    print(`${segment._id.engagement} | ${segment._id.reviewer} | ${segment._id.loyalty}:`);
    print(`  Users: ${segment.userCount}`);
    print(`  Avg Check-ins: ${segment.avgCheckins.toFixed(1)}`);
    print(`  Avg Reviews: ${segment.avgReviews.toFixed(1)}`);
    print(`  Avg Review Rating: ${segment.avgReviewRating ? segment.avgReviewRating.toFixed(2) : 'N/A'}/5`);
    print(`  Avg Account Age: ${segment.avgAccountAge.toFixed(0)} days`);
    print(`  Avg Days Since Login: ${segment.avgDaysSinceLogin.toFixed(0)} days`);
    print(`  Top Categories: ${segment.topCategories.join(', ')}`);
});

// ===== 3. MARKET OPPORTUNITY ANALYSIS =====
print("\n3. MARKET OPPORTUNITY ANALYSIS");
print("-".repeat(40));

// Identify market gaps and opportunities
print("Analyzing market opportunities and gaps:");

db.events.aggregate([
    {
        $facet: {
            categoryGaps: [
                {
                    $group: {
                        _id: "$category",
                        eventCount: { $sum: 1 },
                        avgPrice: { $avg: "$price" },
                        totalRevenue: { $sum: "$computedStats.totalRevenue" },
                        avgAttendance: { $avg: "$currentAttendees" },
                        freeEvents: { $sum: { $cond: ["$isFree", 1, 0] } }
                    }
                },
                {
                    $addFields: {
                        freeEventPercentage: { $multiply: [{ $divide: ["$freeEvents", "$eventCount"] }, 100] },
                        revenuePerEvent: { $divide: ["$totalRevenue", "$eventCount"] },
                        marketSaturation: {
                            $switch: {
                                branches: [
                                    { case: { $lt: ["$eventCount", 5] }, then: "Underserved" },
                                    { case: { $lt: ["$eventCount", 15] }, then: "Emerging" },
                                    { case: { $lt: ["$eventCount", 30] }, then: "Growing" }
                                ],
                                default: "Saturated"
                            }
                        }
                    }
                },
                { $sort: { eventCount: 1 } }
            ],
            priceOpportunities: [
                {
                    $match: { price: { $gt: 0 } }
                },
                {
                    $group: {
                        _id: {
                            category: "$category",
                            priceRange: {
                                $switch: {
                                    branches: [
                                        { case: { $lt: ["$price", 25] }, then: "Budget ($0-$24)" },
                                        { case: { $lt: ["$price", 75] }, then: "Mid-range ($25-$74)" },
                                        { case: { $lt: ["$price", 150] }, then: "Premium ($75-$149)" }
                                    ],
                                    default: "Luxury ($150+)"
                                }
                            }
                        },
                        eventCount: { $sum: 1 },
                        avgAttendance: { $avg: "$currentAttendees" },
                        avgRevenue: { $avg: "$computedStats.totalRevenue" }
                    }
                },
                { $sort: { "_id.category": 1, "_id.priceRange": 1 } }
            ],
            geographicOpportunities: [
                {
                    $addFields: {
                        region: {
                            $switch: {
                                branches: [
                                    {
                                        case: {
                                            $and: [
                                                { $gte: ["$location.coordinates.0", -123.3] },
                                                { $lte: ["$location.coordinates.0", -123.0] },
                                                { $gte: ["$location.coordinates.1", 49.2] },
                                                { $lte: ["$location.coordinates.1", 49.3] }
                                            ]
                                        },
                                        then: "Vancouver Metro"
                                    },
                                    {
                                        case: {
                                            $and: [
                                                { $gte: ["$location.coordinates.0", -124.1] },
                                                { $lte: ["$location.coordinates.0", -123.8] },
                                                { $gte: ["$location.coordinates.1", 49.0] },
                                                { $lte: ["$location.coordinates.1", 49.2] }
                                            ]
                                        },
                                        then: "Vancouver Island"
                                    }
                                ],
                                default: "Other BC"
                            }
                        }
                    }
                },
                {
                    $group: {
                        _id: {
                            region: "$region",
                            category: "$category"
                        },
                        eventCount: { $sum: 1 },
                        avgPrice: { $avg: "$price" },
                        totalRevenue: { $sum: "$computedStats.totalRevenue" }
                    }
                },
                { $sort: { eventCount: 1 } }
            ]
        }
    }
]).forEach(analysis => {
    print("CATEGORY MARKET ANALYSIS:");
    analysis.categoryGaps.forEach(category => {
        print(`${category._id} (${category.marketSaturation}):`);
        print(`  Events: ${category.eventCount}`);
        print(`  Avg Price: $${category.avgPrice.toFixed(2)} CAD`);
        print(`  Revenue/Event: $${category.revenuePerEvent.toFixed(2)} CAD`);
        print(`  Avg Attendance: ${category.avgAttendance.toFixed(0)}`);
        print(`  Free Events: ${category.freeEventPercentage.toFixed(1)}%`);
    });
    
    print("\nPRICE POINT OPPORTUNITIES:");
    let currentCategory = "";
    analysis.priceOpportunities.forEach(price => {
        if (price._id.category !== currentCategory) {
            print(`\n${price._id.category}:`);
            currentCategory = price._id.category;
        }
        print(`  ${price._id.priceRange}: ${price.eventCount} events, avg ${price.avgAttendance.toFixed(0)} attendees`);
    });
    
    print("\nGEOGRAPHIC OPPORTUNITIES:");
    let currentRegion = "";
    analysis.geographicOpportunities.slice(0, 15).forEach(geo => {
        if (geo._id.region !== currentRegion) {
            print(`\n${geo._id.region}:`);
            currentRegion = geo._id.region;
        }
        print(`  ${geo._id.category}: ${geo.eventCount} events, $${geo.totalRevenue.toFixed(0)} revenue`);
    });
});

// ===== 4. COMPETITIVE ANALYSIS =====
print("\n4. COMPETITIVE ANALYSIS");
print("-".repeat(40));

// Analyze competitive landscape by organizer
print("Analyzing competitive landscape:");

db.events.aggregate([
    {
        $match: {
            organizer: { $ne: null },
            status: { $in: ["published", "completed"] }
        }
    },
    {
        $group: {
            _id: "$organizer",
            eventCount: { $sum: 1 },
            categories: { $addToSet: "$category" },
            eventTypes: { $addToSet: "$eventType" },
            totalRevenue: { $sum: "$computedStats.totalRevenue" },
            avgPrice: { $avg: "$price" },
            avgAttendance: { $avg: "$currentAttendees" },
            avgRating: { $avg: "$computedStats.averageRating" },
            totalReviews: { $sum: "$computedStats.reviewCount" }
        }
    },
    {
        $addFields: {
            marketShare: { $divide: ["$totalRevenue", { $sum: "$totalRevenue" }] },
            diversificationScore: { $size: "$categories" },
            avgRevenuePerEvent: { $divide: ["$totalRevenue", "$eventCount"] },
            competitiveRank: {
                $add: [
                    { $multiply: ["$eventCount", 0.3] },
                    { $multiply: ["$totalRevenue", 0.0001] },
                    { $multiply: [{ $ifNull: ["$avgRating", 3] }, 2] },
                    { $multiply: [{ $size: "$categories" }, 1] }
                ]
            }
        }
    },
    {
        $match: { eventCount: { $gte: 2 } }
    },
    {
        $sort: { competitiveRank: -1 }
    },
    {
        $limit: 10
    }
]).forEach(organizer => {
    print(`${organizer._id}:`);
    print(`  Events: ${organizer.eventCount}`);
    print(`  Categories: ${organizer.categories.join(', ')}`);
    print(`  Event Types: ${organizer.eventTypes.join(', ')}`);
    print(`  Total Revenue: $${organizer.totalRevenue.toFixed(2)} CAD`);
    print(`  Avg Revenue/Event: $${organizer.avgRevenuePerEvent.toFixed(2)} CAD`);
    print(`  Avg Price: $${organizer.avgPrice.toFixed(2)} CAD`);
    print(`  Avg Attendance: ${organizer.avgAttendance.toFixed(0)}`);
    print(`  Avg Rating: ${organizer.avgRating ? organizer.avgRating.toFixed(2) : 'N/A'}/5`);
    print(`  Diversification Score: ${organizer.diversificationScore}`);
    print(`  Competitive Rank: ${organizer.competitiveRank.toFixed(2)}`);
});

// ===== 5. TREND ANALYSIS =====
print("\n5. TREND ANALYSIS");
print("-".repeat(40));

// Analyze trends over time
print("Analyzing market trends and patterns:");

db.events.aggregate([
    {
        $addFields: {
            createdMonth: { $dateToString: { format: "%Y-%m", date: "$createdAt" } },
            eventMonth: { $dateToString: { format: "%Y-%m", date: "$startDate" } },
            leadTime: {
                $divide: [
                    { $subtract: ["$startDate", "$createdAt"] },
                    86400000
                ]
            }
        }
    },
    {
        $facet: {
            creationTrends: [
                {
                    $group: {
                        _id: "$createdMonth",
                        eventsCreated: { $sum: 1 },
                        categories: { $addToSet: "$category" },
                        eventTypes: { $addToSet: "$eventType" },
                        avgPrice: { $avg: "$price" },
                        freeEvents: { $sum: { $cond: ["$isFree", 1, 0] } }
                    }
                },
                {
                    $addFields: {
                        freeEventPercentage: { $multiply: [{ $divide: ["$freeEvents", "$eventsCreated"] }, 100] }
                    }
                },
                { $sort: { _id: 1 } }
            ],
            eventTypeTrends: [
                {
                    $group: {
                        _id: {
                            month: "$eventMonth",
                            eventType: "$eventType"
                        },
                        count: { $sum: 1 },
                        avgPrice: { $avg: "$price" }
                    }
                },
                { $sort: { "_id.month": 1, "_id.eventType": 1 } }
            ],
            leadTimeTrends: [
                {
                    $match: { leadTime: { $gte: 0, $lte: 365 } }
                },
                {
                    $group: {
                        _id: "$category",
                        avgLeadTime: { $avg: "$leadTime" },
                        minLeadTime: { $min: "$leadTime" },
                        maxLeadTime: { $max: "$leadTime" },
                        eventCount: { $sum: 1 }
                    }
                },
                { $sort: { avgLeadTime: -1 } }
            ]
        }
    }
]).forEach(analysis => {
    print("EVENT CREATION TRENDS:");
    analysis.creationTrends.forEach(month => {
        print(`${month._id}:`);
        print(`  Events Created: ${month.eventsCreated}`);
        print(`  Categories: ${month.categories.length} different`);
        print(`  Event Types: ${month.eventTypes.join(', ')}`);
        print(`  Avg Price: $${month.avgPrice.toFixed(2)} CAD`);
        print(`  Free Events: ${month.freeEventPercentage.toFixed(1)}%`);
    });
    
    print("\nEVENT TYPE TRENDS:");
    let currentMonth = "";
    analysis.eventTypeTrends.forEach(trend => {
        if (trend._id.month !== currentMonth) {
            print(`\n${trend._id.month}:`);
            currentMonth = trend._id.month;
        }
        print(`  ${trend._id.eventType}: ${trend.count} events, avg $${trend.avgPrice.toFixed(2)}`);
    });
    
    print("\nPLANNING LEAD TIME BY CATEGORY:");
    analysis.leadTimeTrends.forEach(lead => {
        print(`${lead._id}:`);
        print(`  Avg Lead Time: ${lead.avgLeadTime.toFixed(0)} days`);
        print(`  Range: ${lead.minLeadTime.toFixed(0)} - ${lead.maxLeadTime.toFixed(0)} days`);
        print(`  Sample Size: ${lead.eventCount} events`);
    });
});

print("\nBusiness Intelligence Analysis completed successfully!");
print("=".repeat(60));
