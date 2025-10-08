// Text Search Aggregation Pipelines for EventSphere
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("=".repeat(60));
print("TEXT SEARCH AGGREGATION PIPELINES");
print("=".repeat(60));

// ===== 1. BASIC TEXT SEARCH WITH RELEVANCE =====
print("\n1. BASIC TEXT SEARCH WITH RELEVANCE");
print("-".repeat(40));

// Search for technology-related events with relevance scoring
print("Searching for 'technology conference' events:");
db.events.aggregate([
    {
        $match: {
            $text: { $search: "technology conference" }
        }
    },
    {
        $addFields: {
            relevanceScore: { $meta: "textScore" }
        }
    },
    {
        $lookup: {
            from: "venues",
            localField: "venueId",
            foreignField: "_id",
            as: "venue"
        }
    },
    {
        $project: {
            title: 1,
            description: 1,
            category: 1,
            eventType: 1,
            startDate: 1,
            price: 1,
            relevanceScore: 1,
            venueName: { $arrayElemAt: ["$venue.name", 0] },
            tags: 1
        }
    },
    {
        $sort: { relevanceScore: { $meta: "textScore" }, startDate: 1 }
    },
    {
        $limit: 5
    }
]).forEach(event => {
    print(`- ${event.title} (Score: ${event.relevanceScore.toFixed(2)})`);
    print(`  Category: ${event.category} | Type: ${event.eventType}`);
    print(`  Price: $${event.price || 0} CAD | Date: ${event.startDate.toISOString().split('T')[0]}`);
    print(`  Venue: ${event.venueName || 'Custom Location'}`);
    print(`  Tags: ${event.tags ? event.tags.join(', ') : 'None'}`);
    print(`  Description: ${event.description ? event.description.substring(0, 100) + '...' : 'N/A'}`);
});

// ===== 2. ADVANCED TEXT SEARCH WITH FILTERS =====
print("\n2. ADVANCED TEXT SEARCH WITH FILTERS");
print("-".repeat(40));

// Search with text and additional filters
print("Searching for 'music jazz' events with price and date filters:");
db.events.aggregate([
    {
        $match: {
            $and: [
                { $text: { $search: "music jazz" } },
                { price: { $lte: 50 } },
                { startDate: { $gte: new Date("2025-10-01") } },
                { status: "published" }
            ]
        }
    },
    {
        $addFields: {
            relevanceScore: { $meta: "textScore" },
            matchedTerms: {
                $size: {
                    $setIntersection: [
                        { $split: [{ $toLower: "$title" }, " "] },
                        ["music", "jazz", "concert", "performance"]
                    ]
                }
            }
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
        $addFields: {
            avgRating: { $avg: "$reviews.rating" },
            reviewCount: { $size: "$reviews" }
        }
    },
    {
        $project: {
            title: 1,
            category: 1,
            eventType: 1,
            startDate: 1,
            price: 1,
            isFree: 1,
            relevanceScore: 1,
            matchedTerms: 1,
            avgRating: 1,
            reviewCount: 1,
            tags: 1,
            "venueReference.name": 1,
            "venueReference.city": 1
        }
    },
    {
        $sort: { 
            relevanceScore: { $meta: "textScore" },
            matchedTerms: -1,
            avgRating: -1
        }
    }
]).forEach(event => {
    print(`- ${event.title} (Score: ${event.relevanceScore.toFixed(2)}, Matches: ${event.matchedTerms})`);
    print(`  Category: ${event.category} | Price: ${event.isFree ? 'FREE' : '$' + event.price + ' CAD'}`);
    print(`  Rating: ${event.avgRating ? event.avgRating.toFixed(1) : 'N/A'}/5 (${event.reviewCount} reviews)`);
    print(`  Venue: ${event.venueReference?.name || 'Custom Location'} - ${event.venueReference?.city || 'Unknown'}`);
    print(`  Date: ${event.startDate.toISOString().split('T')[0]}`);
});

// ===== 3. TEXT SEARCH ANALYTICS =====
print("\n3. TEXT SEARCH ANALYTICS");
print("-".repeat(40));

// Analyze search term frequency and relevance
print("Analyzing text search patterns and term frequency:");
db.events.aggregate([
    {
        $match: {
            $or: [
                { $text: { $search: "technology" } },
                { $text: { $search: "music" } },
                { $text: { $search: "food" } },
                { $text: { $search: "business" } },
                { $text: { $search: "health" } }
            ]
        }
    },
    {
        $addFields: {
            relevanceScore: { $meta: "textScore" },
            titleWords: { $split: [{ $toLower: "$title" }, " "] },
            descWords: { $split: [{ $toLower: "$description" }, " "] },
            searchTerms: {
                $setIntersection: [
                    { $concatArrays: [
                        { $split: [{ $toLower: "$title" }, " "] },
                        { $split: [{ $toLower: "$description" }, " "] },
                        { $map: { input: "$tags", as: "tag", in: { $toLower: "$$tag" } } }
                    ]},
                    ["technology", "music", "food", "business", "health", "conference", "workshop", "festival"]
                ]
            }
        }
    },
    {
        $unwind: "$searchTerms"
    },
    {
        $group: {
            _id: "$searchTerms",
            eventCount: { $sum: 1 },
            avgRelevanceScore: { $avg: "$relevanceScore" },
            categories: { $addToSet: "$category" },
            eventTypes: { $addToSet: "$eventType" },
            avgPrice: { $avg: "$price" },
            totalRevenue: { $sum: "$computedStats.totalRevenue" }
        }
    },
    {
        $match: { eventCount: { $gte: 2 } }
    },
    {
        $sort: { eventCount: -1, avgRelevanceScore: -1 }
    }
]).forEach(term => {
    print(`"${term._id}":`);
    print(`  Events: ${term.eventCount}`);
    print(`  Avg Relevance Score: ${term.avgRelevanceScore.toFixed(2)}`);
    print(`  Categories: ${term.categories.join(', ')}`);
    print(`  Event Types: ${term.eventTypes.join(', ')}`);
    print(`  Avg Price: $${term.avgPrice.toFixed(2)} CAD`);
    print(`  Total Revenue: $${term.totalRevenue.toFixed(2)} CAD`);
});

// ===== 4. FUZZY TEXT MATCHING =====
print("\n4. FUZZY TEXT MATCHING");
print("-".repeat(40));

// Simulate fuzzy matching using regex and text search
print("Performing fuzzy text matching for event discovery:");
db.events.aggregate([
    {
        $addFields: {
            titleLower: { $toLower: "$title" },
            descLower: { $toLower: "$description" },
            fuzzyMatches: {
                $add: [
                    { $cond: [{ $regexMatch: { input: "$title", regex: /tech|technolog/i } }, 2, 0] },
                    { $cond: [{ $regexMatch: { input: "$title", regex: /music|concert|jazz/i } }, 2, 0] },
                    { $cond: [{ $regexMatch: { input: "$description", regex: /network|connect/i } }, 1, 0] },
                    { $cond: [{ $regexMatch: { input: "$description", regex: /learn|education/i } }, 1, 0] },
                    { $cond: [{ $in: ["networking", "$tags"] }, 1, 0] },
                    { $cond: [{ $in: ["educational", "$tags"] }, 1, 0] }
                ]
            }
        }
    },
    {
        $match: { fuzzyMatches: { $gte: 2 } }
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
            popularityScore: {
                $add: [
                    "$fuzzyMatches",
                    { $multiply: [{ $size: "$checkins" }, 0.1] },
                    { $cond: [{ $gte: ["$computedStats.averageRating", 4] }, 1, 0] }
                ]
            }
        }
    },
    {
        $project: {
            title: 1,
            category: 1,
            eventType: 1,
            startDate: 1,
            price: 1,
            fuzzyMatches: 1,
            popularityScore: 1,
            actualAttendees: 1,
            tags: 1,
            "computedStats.averageRating": 1
        }
    },
    {
        $sort: { popularityScore: -1, fuzzyMatches: -1 }
    },
    {
        $limit: 8
    }
]).forEach(event => {
    print(`- ${event.title}`);
    print(`  Fuzzy Score: ${event.fuzzyMatches} | Popularity: ${event.popularityScore.toFixed(1)}`);
    print(`  Category: ${event.category} | Attendees: ${event.actualAttendees}`);
    print(`  Rating: ${event.computedStats?.averageRating || 'N/A'}/5`);
    print(`  Tags: ${event.tags ? event.tags.join(', ') : 'None'}`);
});

// ===== 5. CATEGORY-BASED TEXT SEARCH =====
print("\n5. CATEGORY-BASED TEXT SEARCH");
print("-".repeat(40));

// Search within specific categories with text relevance
print("Performing category-specific text searches:");
db.events.aggregate([
    {
        $facet: {
            technologyEvents: [
                { $match: { 
                    category: "Technology",
                    $text: { $search: "AI machine learning workshop conference" }
                }},
                { $addFields: { relevanceScore: { $meta: "textScore" } }},
                { $sort: { relevanceScore: { $meta: "textScore" } }},
                { $limit: 3 }
            ],
            musicEvents: [
                { $match: { 
                    category: "Music",
                    $text: { $search: "jazz classical concert performance" }
                }},
                { $addFields: { relevanceScore: { $meta: "textScore" } }},
                { $sort: { relevanceScore: { $meta: "textScore" } }},
                { $limit: 3 }
            ],
            businessEvents: [
                { $match: { 
                    category: "Business",
                    $text: { $search: "networking startup entrepreneur conference" }
                }},
                { $addFields: { relevanceScore: { $meta: "textScore" } }},
                { $sort: { relevanceScore: { $meta: "textScore" } }},
                { $limit: 3 }
            ]
        }
    }
]).forEach(results => {
    print("Technology Events:");
    results.technologyEvents.forEach(event => {
        print(`  - ${event.title} (Score: ${event.relevanceScore.toFixed(2)})`);
    });
    
    print("\nMusic Events:");
    results.musicEvents.forEach(event => {
        print(`  - ${event.title} (Score: ${event.relevanceScore.toFixed(2)})`);
    });
    
    print("\nBusiness Events:");
    results.businessEvents.forEach(event => {
        print(`  - ${event.title} (Score: ${event.relevanceScore.toFixed(2)})`);
    });
});

// ===== 6. SEARCH RECOMMENDATION ENGINE =====
print("\n6. SEARCH RECOMMENDATION ENGINE");
print("-".repeat(40));

// Build recommendations based on text similarity and user preferences
print("Building search-based event recommendations:");
db.events.aggregate([
    {
        $match: {
            status: "published",
            startDate: { $gte: new Date() }
        }
    },
    {
        $addFields: {
            textFeatures: {
                $concatArrays: [
                    { $split: [{ $toLower: "$title" }, " "] },
                    { $split: [{ $toLower: "$category" }, " "] },
                    { $map: { input: "$tags", as: "tag", in: { $toLower: "$$tag" } } }
                ]
            }
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
            avgRating: { $avg: "$reviews.rating" },
            reviewCount: { $size: "$reviews" },
            attendeeCount: { $size: "$checkins" },
            recommendationScore: {
                $add: [
                    { $multiply: [{ $ifNull: [{ $avg: "$reviews.rating" }, 3] }, 2] },
                    { $multiply: [{ $size: "$reviews" }, 0.5] },
                    { $multiply: [{ $size: "$checkins" }, 0.1] },
                    { $cond: [{ $eq: ["$isFree", true] }, 2, 0] },
                    { $cond: [{ $in: ["networking", "$tags"] }, 1, 0] },
                    { $cond: [{ $in: ["educational", "$tags"] }, 1, 0] }
                ]
            }
        }
    },
    {
        $group: {
            _id: "$category",
            events: {
                $push: {
                    title: "$title",
                    eventType: "$eventType",
                    startDate: "$startDate",
                    price: "$price",
                    isFree: "$isFree",
                    avgRating: "$avgRating",
                    reviewCount: "$reviewCount",
                    attendeeCount: "$attendeeCount",
                    recommendationScore: "$recommendationScore",
                    tags: "$tags"
                }
            },
            avgRecommendationScore: { $avg: "$recommendationScore" },
            totalEvents: { $sum: 1 }
        }
    },
    {
        $addFields: {
            topEvents: {
                $slice: [
                    {
                        $sortArray: {
                            input: "$events",
                            sortBy: { recommendationScore: -1 }
                        }
                    },
                    2
                ]
            }
        }
    },
    {
        $sort: { avgRecommendationScore: -1 }
    }
]).forEach(category => {
    print(`${category._id} (${category.totalEvents} events, avg score: ${category.avgRecommendationScore.toFixed(2)}):`);
    category.topEvents.forEach(event => {
        print(`  - ${event.title} (Score: ${event.recommendationScore.toFixed(2)})`);
        print(`    Type: ${event.eventType} | Price: ${event.isFree ? 'FREE' : '$' + event.price + ' CAD'}`);
        print(`    Rating: ${event.avgRating ? event.avgRating.toFixed(1) : 'N/A'}/5 | Attendees: ${event.attendeeCount}`);
        print(`    Tags: ${event.tags ? event.tags.slice(0, 3).join(', ') : 'None'}`);
    });
});

// ===== 7. SEARCH PERFORMANCE ANALYSIS =====
print("\n7. SEARCH PERFORMANCE ANALYSIS");
print("-".repeat(40));

// Analyze text search index effectiveness
print("Analyzing text search index effectiveness:");
db.events.aggregate([
    {
        $sample: { size: 100 } // Sample for performance analysis
    },
    {
        $addFields: {
            titleWordCount: { $size: { $split: ["$title", " "] } },
            descWordCount: { $size: { $split: [{ $ifNull: ["$description", ""] }, " "] } },
            tagCount: { $size: { $ifNull: ["$tags", []] } },
            searchableContent: {
                $concat: [
                    "$title", " ",
                    { $ifNull: ["$description", ""] }, " ",
                    "$category", " ",
                    { $reduce: {
                        input: { $ifNull: ["$tags", []] },
                        initialValue: "",
                        in: { $concat: ["$$value", " ", "$$this"] }
                    }}
                ]
            }
        }
    },
    {
        $addFields: {
            totalSearchableWords: { $size: { $split: ["$searchableContent", " "] } },
            searchDensity: {
                $divide: [
                    { $add: ["$titleWordCount", "$descWordCount", "$tagCount"] },
                    { $max: [{ $size: { $split: ["$searchableContent", " "] } }, 1] }
                ]
            }
        }
    },
    {
        $group: {
            _id: "$category",
            avgTitleWords: { $avg: "$titleWordCount" },
            avgDescWords: { $avg: "$descWordCount" },
            avgTagCount: { $avg: "$tagCount" },
            avgSearchableWords: { $avg: "$totalSearchableWords" },
            avgSearchDensity: { $avg: "$searchDensity" },
            eventCount: { $sum: 1 }
        }
    },
    {
        $sort: { avgSearchDensity: -1 }
    }
]).forEach(category => {
    print(`${category._id}:`);
    print(`  Events Analyzed: ${category.eventCount}`);
    print(`  Avg Title Words: ${category.avgTitleWords.toFixed(1)}`);
    print(`  Avg Description Words: ${category.avgDescWords.toFixed(1)}`);
    print(`  Avg Tag Count: ${category.avgTagCount.toFixed(1)}`);
    print(`  Avg Total Searchable Words: ${category.avgSearchableWords.toFixed(1)}`);
    print(`  Search Density Score: ${category.avgSearchDensity.toFixed(3)}`);
});

print("\nText Search Aggregation Pipelines completed successfully!");
print("=".repeat(60));
