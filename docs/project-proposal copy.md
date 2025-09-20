# **CSCI 485:** *MongoDB Project Proposal*

#### **Student ID:** 664 870 797
#### **Student name:** Chris Lawrence

### **Project Title:** Event Discovery and Check-In System with Geospatial Analytics

### **Domain:** Social and Event Management

## **Reason for Selection:**
Events and meetups are crucial for modern social and professional life. I chose this project because it demonstrates real-world data complexity with users, venues, events, tickets, and check-ins that naturally require flexible, evolving schemas. Event management applications are common in industry, providing practical experience with data modeling, performance optimization, and advanced MongoDB features that directly map to production systems.

## **Why NoSQL (MongoDB) is a Good Fit:**
MongoDB excels for this project due to event data's inherent variability. Each event includes unique attributes like location coordinates, dynamic pricing tiers, embedded attendee lists, and flexible metadata. A relational model would require numerous normalized tables and complex joins, while MongoDB's document structure allows storing diverse event data with embedded subdocuments (tickets, check-ins) and references for users and venues.

## **Key MongoDB Features Demonstrated:**
- **Geospatial Queries**: 2dsphere indexes with $geoNear aggregation for finding nearby events within specified radii, supporting interactive map visualization
- **Text Search**: Multi-field text indexes enabling full-text search across event titles, descriptions, and tags with relevance scoring
- **Aggregation Pipelines**: Complex analytics including revenue tracking, venue performance metrics, and temporal event analysis
- **Transactions**: Atomic ticket booking operations ensuring data consistency during high-concurrency scenarios
- **Schema Flexibility**: Dynamic event attributes and embedded documents for tickets and check-ins without rigid table structures

This project showcases comprehensive MongoDB capabilities including CRUD operations, advanced indexing strategies, geospatial analytics, and real-time data processing, resulting in both strong academic outcomes and a portfolio-ready system.


---


- 4+ collections, 
- 1000+ records, 
- CRUD + aggregations, 
- indexes, text search, 
- transactions, and 
- possibly geospatial queries

Requirements:
- **Fits MongoDB well** (flexible schema, semi-structured/unstructured data, evolving records).
- **Is industry-relevant** (employers recognize it as useful).
- **Has room for interesting queries & analytics** (so you can show off aggregations, indexes, text search, geospatial).
- **Can be demoed cleanly** (a dataset and maybe a small front-end/API).


**Event Discovery & Check-In System (Concerts, Meetups, Conferences)**

- Events have dynamic structures (location, performers, sponsors, tickets). Users and organizers interact in flexible ways.
- Relevant for event companies (Ticketmaster, Meetup, Eventbrite).
- Possible features ?:
    - Collections: `users`, `events`, `venues`, `tickets`, `checkins`.
    - Geospatial queries to find nearby events.
    - Aggregations for event attendance stats.
    - Text search for events by title/description. case insensitive partial match
    - Transactions for ticket booking
    - Future expansion could be users selling tickets to each other