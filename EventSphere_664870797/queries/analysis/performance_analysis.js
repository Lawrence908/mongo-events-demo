// Performance Analysis Queries for EventSphere
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("=".repeat(60));
print("PERFORMANCE ANALYSIS QUERIES");
print("=".repeat(60));

// ===== 1. INDEX USAGE ANALYSIS =====
print("\n1. INDEX USAGE ANALYSIS");
print("-".repeat(40));

// Analyze index usage and performance
print("Analyzing index usage patterns:");

// Test geospatial query performance
print("\nTesting geospatial query performance:");
const geoStartTime = new Date();
const geoResults = db.events.find({
    location: {
        $near: {
            $geometry: { type: "Point", coordinates: [-123.1207, 49.2827] },
            $maxDistance: 50000
        }
    }
}).limit(10).toArray();
const geoEndTime = new Date();
print(`Geospatial query: ${geoResults.length} results in ${geoEndTime - geoStartTime}ms`);

// Test text search performance
print("\nTesting text search performance:");
const textStartTime = new Date();
const textResults = db.events.find({
    $text: { $search: "technology conference" }
}).limit(10).toArray();
const textEndTime = new Date();
print(`Text search query: ${textResults.length} results in ${textEndTime - textStartTime}ms`);

// Test compound index performance
print("\nTesting compound index performance:");
const compoundStartTime = new Date();
const compoundResults = db.events.find({
    category: "Technology",
    startDate: { $gte: new Date("2025-01-01") }
}).limit(10).toArray();
const compoundEndTime = new Date();
print(`Compound index query: ${compoundResults.length} results in ${compoundEndTime - compoundStartTime}ms`);

// Analyze query execution plans
print("\nAnalyzing query execution plans:");

// Geospatial query explain
print("Geospatial query execution plan:");
const geoExplain = db.events.find({
    location: {
        $near: {
            $geometry: { type: "Point", coordinates: [-123.1207, 49.2827] },
            $maxDistance: 50000
        }
    }
}).limit(5).explain("executionStats");

print(`  Stage: ${geoExplain.executionStats.executionStages.stage}`);
print(`  Index Used: ${geoExplain.executionStats.executionStages.indexName || 'None'}`);
print(`  Docs Examined: ${geoExplain.executionStats.totalDocsExamined}`);
print(`  Docs Returned: ${geoExplain.executionStats.totalDocsReturned}`);
print(`  Execution Time: ${geoExplain.executionStats.executionTimeMillis}ms`);

// Text search query explain
print("\nText search query execution plan:");
const textExplain = db.events.find({
    $text: { $search: "technology" }
}).limit(5).explain("executionStats");

print(`  Stage: ${textExplain.executionStats.executionStages.stage}`);
print(`  Index Used: ${textExplain.executionStats.executionStages.indexName || 'None'}`);
print(`  Docs Examined: ${textExplain.executionStats.totalDocsExamined}`);
print(`  Docs Returned: ${textExplain.executionStats.totalDocsReturned}`);
print(`  Execution Time: ${textExplain.executionStats.executionTimeMillis}ms`);

// ===== 2. COLLECTION STATISTICS =====
print("\n2. COLLECTION STATISTICS");
print("-".repeat(40));

// Get collection statistics
print("Collection size and performance statistics:");

const collections = ["events", "venues", "users", "reviews", "checkins"];
collections.forEach(collectionName => {
    const stats = db.getCollection(collectionName).stats();
    print(`\n${collectionName.toUpperCase()} Collection:`);
    print(`  Documents: ${stats.count.toLocaleString()}`);
    print(`  Avg Document Size: ${(stats.avgObjSize / 1024).toFixed(2)} KB`);
    print(`  Total Size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
    print(`  Storage Size: ${(stats.storageSize / 1024 / 1024).toFixed(2)} MB`);
    print(`  Indexes: ${stats.nindexes}`);
    print(`  Index Size: ${(stats.totalIndexSize / 1024 / 1024).toFixed(2)} MB`);
});

// ===== 3. QUERY PERFORMANCE BENCHMARKS =====
print("\n3. QUERY PERFORMANCE BENCHMARKS");
print("-".repeat(40));

// Benchmark common query patterns
print("Benchmarking common query patterns:");

const benchmarkQueries = [
    {
        name: "Find events by category",
        query: () => db.events.find({ category: "Technology" }).limit(10).toArray()
    },
    {
        name: "Find events by date range",
        query: () => db.events.find({
            startDate: { $gte: new Date("2025-01-01"), $lte: new Date("2025-12-31") }
        }).limit(10).toArray()
    },
    {
        name: "Find events with venue lookup",
        query: () => db.events.aggregate([
            { $match: { venueId: { $ne: null } } },
            { $lookup: { from: "venues", localField: "venueId", foreignField: "_id", as: "venue" } },
            { $limit: 10 }
        ]).toArray()
    },
    {
        name: "Find events with reviews",
        query: () => db.events.aggregate([
            { $lookup: { from: "reviews", localField: "_id", foreignField: "eventId", as: "reviews" } },
            { $match: { "reviews.0": { $exists: true } } },
            { $limit: 10 }
        ]).toArray()
    },
    {
        name: "Complex aggregation - event analytics",
        query: () => db.events.aggregate([
            { $match: { status: "published" } },
            { $group: { _id: "$category", count: { $sum: 1 }, avgPrice: { $avg: "$price" } } },
            { $sort: { count: -1 } }
        ]).toArray()
    }
];

benchmarkQueries.forEach(benchmark => {
    const iterations = 5;
    let totalTime = 0;
    let results = 0;
    
    for (let i = 0; i < iterations; i++) {
        const startTime = new Date();
        const queryResults = benchmark.query();
        const endTime = new Date();
        totalTime += (endTime - startTime);
        if (i === 0) results = queryResults.length;
    }
    
    const avgTime = totalTime / iterations;
    print(`${benchmark.name}:`);
    print(`  Avg Time: ${avgTime.toFixed(2)}ms (${iterations} iterations)`);
    print(`  Results: ${results} documents`);
    print(`  Performance: ${(results / avgTime * 1000).toFixed(0)} docs/second`);
});

// ===== 4. AGGREGATION PERFORMANCE =====
print("\n4. AGGREGATION PERFORMANCE");
print("-".repeat(40));

// Test complex aggregation performance
print("Testing complex aggregation performance:");

const complexAggregations = [
    {
        name: "Event analytics with lookups",
        pipeline: [
            { $match: { status: "published" } },
            { $lookup: { from: "reviews", localField: "_id", foreignField: "eventId", as: "reviews" } },
            { $lookup: { from: "checkins", localField: "_id", foreignField: "eventId", as: "checkins" } },
            { $addFields: {
                avgRating: { $avg: "$reviews.rating" },
                attendeeCount: { $size: "$checkins" }
            }},
            { $group: {
                _id: "$category",
                eventCount: { $sum: 1 },
                avgRating: { $avg: "$avgRating" },
                totalAttendees: { $sum: "$attendeeCount" }
            }},
            { $sort: { totalAttendees: -1 } }
        ]
    },
    {
        name: "Geospatial aggregation",
        pipeline: [
            { $geoNear: {
                near: { type: "Point", coordinates: [-123.1207, 49.2827] },
                distanceField: "distance",
                maxDistance: 100000,
                spherical: true
            }},
            { $group: {
                _id: {
                    $switch: {
                        branches: [
                            { case: { $lte: ["$distance", 10000] }, then: "0-10km" },
                            { case: { $lte: ["$distance", 25000] }, then: "10-25km" },
                            { case: { $lte: ["$distance", 50000] }, then: "25-50km" }
                        ],
                        default: "50km+"
                    }
                },
                count: { $sum: 1 },
                avgPrice: { $avg: "$price" }
            }}
        ]
    },
    {
        name: "User engagement analysis",
        pipeline: [
            { $lookup: { from: "checkins", localField: "_id", foreignField: "userId", as: "checkins" } },
            { $lookup: { from: "reviews", localField: "_id", foreignField: "userId", as: "reviews" } },
            { $addFields: {
                engagementScore: { $add: [{ $size: "$checkins" }, { $multiply: [{ $size: "$reviews" }, 2] }] }
            }},
            { $group: {
                _id: {
                    $switch: {
                        branches: [
                            { case: { $eq: ["$engagementScore", 0] }, then: "Inactive" },
                            { case: { $lte: ["$engagementScore", 3] }, then: "Low" },
                            { case: { $lte: ["$engagementScore", 8] }, then: "Medium" }
                        ],
                        default: "High"
                    }
                },
                userCount: { $sum: 1 },
                avgEngagement: { $avg: "$engagementScore" }
            }}
        ]
    }
];

complexAggregations.forEach(agg => {
    const startTime = new Date();
    const results = db.events.aggregate(agg.pipeline).toArray();
    const endTime = new Date();
    
    print(`${agg.name}:`);
    print(`  Execution Time: ${endTime - startTime}ms`);
    print(`  Results: ${results.length} documents`);
    print(`  Pipeline Stages: ${agg.pipeline.length}`);
});

// ===== 5. MEMORY USAGE ANALYSIS =====
print("\n5. MEMORY USAGE ANALYSIS");
print("-".rect(40));

// Analyze memory usage patterns
print("Analyzing memory usage patterns:");

// Test memory-intensive aggregation
const memoryTestStart = new Date();
const memoryResults = db.events.aggregate([
    { $lookup: { from: "reviews", localField: "_id", foreignField: "eventId", as: "reviews" } },
    { $lookup: { from: "checkins", localField: "_id", foreignField: "eventId", as: "checkins" } },
    { $lookup: { from: "venues", localField: "venueId", foreignField: "_id", as: "venue" } },
    { $addFields: {
        fullEventData: {
            title: "$title",
            reviews: "$reviews",
            checkins: "$checkins",
            venue: { $arrayElemAt: ["$venue", 0] }
        }
    }},
    { $group: {
        _id: "$category",
        events: { $push: "$fullEventData" },
        totalSize: { $sum: { $bsonSize: "$$ROOT" } }
    }},
    { $sort: { totalSize: -1 } }
], { allowDiskUse: true }).toArray();
const memoryTestEnd = new Date();

print(`Memory-intensive aggregation:`);
print(`  Execution Time: ${memoryTestEnd - memoryTestStart}ms`);
print(`  Results: ${memoryResults.length} categories`);
print(`  Used allowDiskUse: true`);

memoryResults.forEach(category => {
    print(`  ${category._id}: ${category.events.length} events, ~${(category.totalSize / 1024).toFixed(2)} KB`);
});

// ===== 6. SCALABILITY ANALYSIS =====
print("\n6. SCALABILITY ANALYSIS");
print("-".repeat(40));

// Analyze how queries scale with data size
print("Analyzing query scalability:");

const scalabilityTests = [
    {
        name: "Linear scan performance",
        query: () => db.events.find({ organizer: { $regex: /Tech/ } }).limit(100).toArray()
    },
    {
        name: "Indexed query performance",
        query: () => db.events.find({ category: "Technology" }).limit(100).toArray()
    },
    {
        name: "Compound index performance",
        query: () => db.events.find({ 
            category: "Technology", 
            startDate: { $gte: new Date("2025-01-01") }
        }).limit(100).toArray()
    }
];

scalabilityTests.forEach(test => {
    const iterations = 3;
    const limits = [10, 50, 100];
    
    print(`\n${test.name}:`);
    limits.forEach(limit => {
        let totalTime = 0;
        for (let i = 0; i < iterations; i++) {
            const startTime = new Date();
            test.query();
            const endTime = new Date();
            totalTime += (endTime - startTime);
        }
        const avgTime = totalTime / iterations;
        print(`  Limit ${limit}: ${avgTime.toFixed(2)}ms avg`);
    });
});

// ===== 7. OPTIMIZATION RECOMMENDATIONS =====
print("\n7. OPTIMIZATION RECOMMENDATIONS");
print("-".repeat(40));

print("Performance optimization recommendations:");

// Analyze slow queries
print("\nSlow query analysis:");
const slowQueries = [
    {
        description: "Full collection scan",
        query: () => db.events.find({ description: { $regex: /conference/i } }).explain("executionStats"),
        recommendation: "Add text index or use $text search instead of regex"
    },
    {
        description: "Unindexed sort",
        query: () => db.events.find({}).sort({ updatedAt: -1 }).limit(10).explain("executionStats"),
        recommendation: "Add index on updatedAt field for sorting"
    },
    {
        description: "Large result set",
        query: () => db.events.find({ status: "published" }).explain("executionStats"),
        recommendation: "Use pagination with limit() and skip() or cursor-based pagination"
    }
];

slowQueries.forEach(test => {
    print(`\n${test.description}:`);
    const explain = test.query();
    print(`  Execution time: ${explain.executionStats.executionTimeMillis}ms`);
    print(`  Documents examined: ${explain.executionStats.totalDocsExamined}`);
    print(`  Documents returned: ${explain.executionStats.totalDocsReturned}`);
    print(`  Index used: ${explain.executionStats.executionStages.indexName || 'None'}`);
    print(`  Recommendation: ${test.recommendation}`);
});

// Index recommendations
print("\nIndex optimization recommendations:");
print("1. Consider partial indexes for frequently filtered fields");
print("2. Use compound indexes for multi-field queries");
print("3. Monitor index usage with db.collection.getIndexes()");
print("4. Remove unused indexes to improve write performance");
print("5. Use sparse indexes for optional fields");
print("6. Consider TTL indexes for time-based data cleanup");

// Query optimization tips
print("\nQuery optimization tips:");
print("1. Use projection to limit returned fields");
print("2. Use $match early in aggregation pipelines");
print("3. Leverage index hints for complex queries");
print("4. Use cursor-based pagination for large datasets");
print("5. Consider read preferences for read-heavy workloads");
print("6. Use allowDiskUse for memory-intensive aggregations");

print("\nPerformance Analysis completed successfully!");
print("=".repeat(60));
