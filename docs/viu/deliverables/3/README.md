# Deliverable 3: Indexing, Workload Analysis & Relationship Design

This directory contains all files for CSCI 485 MongoDB Project Deliverable 3, focusing on performance optimization through strategic indexing, workload analysis, and relationship design for the EventSphere event management system.

## Files Overview

### 📊 Diagrams
- **`er_diagram.puml`** - Entity Relationship diagram showing logical entities and relationships
- **`collection_diagram.puml`** - MongoDB Collection Relationship diagram showing embedding/referencing decisions

### 📋 Documentation
- **`Deliverable3_Report.md`** - Comprehensive deliverable report (PDF content)
- **`index_analysis.md`** - Detailed index analysis with justification table
- **`workload_analysis.md`** - Workload and operations analysis
- **`design_patterns.md`** - Design patterns used and anti-patterns avoided

### 💻 Code Files
- **`create_indexes.js`** - Enhanced index creation script with 32 strategic indexes
- **`sample_queries.js`** - Example queries demonstrating index usage

## Key Achievements

### 🎯 Indexing Strategy
- **32 Strategic Indexes** across all collections
- **Geospatial Optimization** with 2dsphere indexes
- **Text Search** with multi-field relevance scoring
- **Compound Indexes** for common query patterns
- **Polymorphic Indexes** for type-specific filtering

### 📈 Performance Targets
- **Geospatial queries**: < 50ms
- **Text search**: < 100ms
- **Compound queries**: < 75ms
- **Pagination**: < 25ms (cursor-based)
- **Analytics**: < 200ms

### 🏗️ Design Patterns
- **Extended Reference Pattern** - Denormalized venue data for performance
- **Computed Pattern** - Pre-calculated statistics
- **Polymorphic Pattern** - Multiple event/venue types
- **Schema Versioning** - Future-proof design
- **Bridge Collection** - Many-to-many relationships

### 🚫 Anti-Patterns Avoided
- Over-embedding large subdocuments
- Over-indexing (too many indexes)
- Missing indexes on frequent queries
- Using regex without index support
- Inefficient pagination

## How to Use

### 1. Create Diagrams
```bash
# Install PlantUML (if not already installed)
# Then generate diagrams from .puml files
plantuml er_diagram.puml
plantuml collection_diagram.puml
```

### 2. Create Indexes
```bash
# Run the enhanced index creation script
mongo EventSphere create_indexes.js
```

### 3. Test Queries
```bash
# Run sample queries to demonstrate index usage
mongo EventSphere sample_queries.js
```

### 4. Generate PDF Report
Convert `Deliverable3_Report.md` to PDF using your preferred markdown-to-PDF tool.

## Index Summary

| Collection | Index Count | Key Indexes |
|------------|-------------|-------------|
| **events** | 12 | `location: "2dsphere"`, `{category: 1, startDate: 1}`, Text search |
| **venues** | 5 | `location: "2dsphere"`, `{venueType: 1, capacity: 1}` |
| **users** | 3 | `{email: 1}`, `{profile.preferences.location: "2dsphere"}` |
| **reviews** | 6 | `{eventId: 1}`, `{eventId: 1, rating: 1}` |
| **checkins** | 8 | `{eventId: 1, userId: 1}`, `{qrCode: 1}` |

## Performance Characteristics

### Expected Performance (10,000+ events)
- **Geospatial queries**: < 50ms
- **Text search**: < 100ms
- **Compound queries**: < 75ms
- **Pagination**: < 25ms
- **Analytics**: < 200ms

### Index Overhead
- **Total index size**: ~50% of collection size
- **Memory usage**: 60% for indexes, 40% for data
- **Write performance**: Minimal impact with strategic indexing

## Scalability Features

- **Horizontal Scaling**: Sharding by geography or time
- **Index Distribution**: Indexes distributed across shards
- **Query Routing**: Geospatial queries naturally partition
- **Performance Monitoring**: Index usage tracking

## Next Steps

1. **Review Diagrams**: Study the ER and Collection relationship diagrams
2. **Understand Indexes**: Review the index analysis documentation
3. **Run Scripts**: Execute the index creation and sample queries
4. **Generate Report**: Convert the markdown report to PDF
5. **Submit Deliverable**: Package all files for submission

## Contact

**Student**: Chris Lawrence  
**Student ID**: 664 870 797  
**Project**: EventSphere - Event Discovery and Check-In System with Geospatial Analytics
