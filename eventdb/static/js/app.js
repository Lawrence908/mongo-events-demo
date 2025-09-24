// MongoDB Events Demo - Frontend JavaScript

// Global variables
let map = null;
let markers = [];
let currentDb = 'local';
let eventsLayer = null; // GeoJSON layer for nearby results
let socket = null; // Socket.IO client for realtime (EVE-19)

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize database switch
    initializeDatabaseSwitch();
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Load initial data
    loadEvents();
    loadEventsForTickets();
    loadUsersForTickets();

    // Initialize realtime pipeline (EVE-19)
    initializeRealtime();
}

function initializeDatabaseSwitch() {
    const localBtn = document.getElementById('local-db-btn');
    const cloudBtn = document.getElementById('cloud-db-btn');
    const currentDbSpan = document.getElementById('current-db');
    
    localBtn.addEventListener('click', () => switchDatabase('local'));
    cloudBtn.addEventListener('click', () => switchDatabase('cloud'));
    
    // Set initial state
    localBtn.classList.add('active');
}

function switchDatabase(dbType) {
    currentDb = dbType;
    const localBtn = document.getElementById('local-db-btn');
    const cloudBtn = document.getElementById('cloud-db-btn');
    const currentDbSpan = document.getElementById('current-db');
    
    // Update button states
    localBtn.classList.toggle('active', dbType === 'local');
    cloudBtn.classList.toggle('active', dbType === 'cloud');
    
    // Update display
    currentDbSpan.textContent = dbType === 'local' ? 'Local MongoDB' : 'Cloud Atlas';
    
    // Show notification
    showToast(`Switched to ${dbType === 'local' ? 'Local MongoDB' : 'Cloud Atlas'}`, 'info');
    
    // Reload data
    loadEvents();
}

function initializeEventListeners() {
    // CRUD events
    document.getElementById('create-event-form').addEventListener('submit', handleCreateEvent);
    
    // Search events
    document.getElementById('search-btn').addEventListener('click', handleSearch);
    document.getElementById('search-query').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // Nearby events
    document.getElementById('find-nearby-btn').addEventListener('click', handleFindNearby);
    document.getElementById('use-current-location').addEventListener('click', handleUseCurrentLocation);
    document.getElementById('nearby-radius').addEventListener('input', updateRadiusDisplay);
    
    // Analytics
    document.getElementById('load-top-venues').addEventListener('click', loadTopVenues);
    document.getElementById('load-sales-data').addEventListener('click', loadSalesData);
    document.getElementById('load-stats').addEventListener('click', loadGeneralStats);
    
    // Performance
    document.getElementById('explain-query-btn').addEventListener('click', explainQuery);
    document.getElementById('load-indexes').addEventListener('click', loadIndexes);
    
    // Transactions
    document.getElementById('buy-ticket-btn').addEventListener('click', buyTicket);
    document.getElementById('run-txn-demo').addEventListener('click', runTransactionDemo);
    
    // Tab change events
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', handleTabChange);
    });
}

function handleTabChange(event) {
    const target = event.target.getAttribute('data-bs-target');
    
    if (target === '#nearby') {
        initializeMap();
    }
}

// CRUD Functions
async function handleCreateEvent(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const eventData = {
        title: document.getElementById('event-title').value,
        description: document.getElementById('event-description').value,
        tags: document.getElementById('event-tags').value.split(',').map(tag => tag.trim()).filter(tag => tag),
        venueId: '507f1f77bcf86cd799439011', // Placeholder venue ID
        datetime: new Date(document.getElementById('event-datetime').value).toISOString(),
        price: parseFloat(document.getElementById('event-price').value) || null,
        seatsAvailable: parseInt(document.getElementById('event-seats').value)
    };
    
    try {
        const response = await fetch('/events/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventData)
        });
        
        if (response.ok) {
            showToast('Event created successfully!', 'success');
            event.target.reset();
            loadEvents();
        } else {
            const error = await response.json();
            showToast(`Error: ${error.error}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function loadEvents() {
    try {
        const response = await fetch('/events/');
        const data = await response.json();
        
        displayEvents(data.events);
    } catch (error) {
        console.error('Error loading events:', error);
        document.getElementById('events-list').innerHTML = '<p class="text-danger">Error loading events</p>';
    }
}

function displayEvents(events) {
    const container = document.getElementById('events-list');
    
    if (events.length === 0) {
        container.innerHTML = '<p class="text-muted">No events found</p>';
        return;
    }
    
    const html = events.map(event => `
        <div class="event-item">
            <div class="event-title">${event.title}</div>
            <div class="event-description">${event.description || 'No description'}</div>
            <div class="event-meta">
                <strong>Date:</strong> ${new Date(event.datetime).toLocaleString()}<br>
                <strong>Price:</strong> ${event.price ? `$${event.price}` : 'Free'}<br>
                <strong>Seats:</strong> ${event.seatsAvailable}
            </div>
            <div class="event-tags">
                ${event.tags.map(tag => `<span class="event-tag">${tag}</span>`).join('')}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Search Functions
async function handleSearch() {
    const query = document.getElementById('search-query').value.trim();
    
    if (!query) {
        showToast('Please enter a search term', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/events/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        displaySearchResults(data.events, data.query);
    } catch (error) {
        console.error('Error searching events:', error);
        document.getElementById('search-results').innerHTML = '<p class="text-danger">Error searching events</p>';
    }
}

function displaySearchResults(events, query) {
    const container = document.getElementById('search-results');
    
    if (events.length === 0) {
        container.innerHTML = '<p class="text-muted">No events found for your search</p>';
        return;
    }
    
    const html = events.map(event => `
        <div class="search-result">
            <div class="event-title">${event.title}</div>
            <div class="event-description">${event.description || 'No description'}</div>
            <div class="event-meta">
                <strong>Date:</strong> ${new Date(event.datetime).toLocaleString()}<br>
                <strong>Price:</strong> ${event.price ? `$${event.price}` : 'Free'}<br>
                <strong>Seats:</strong> ${event.seatsAvailable}
            </div>
            ${event.score ? `<div class="search-score">Relevance Score: ${event.score.toFixed(2)}</div>` : ''}
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Geospatial Functions
function initializeMap() {
    if (map) return; // Map already initialized
    
    map = L.map('map').setView([40.7128, -74.0060], 10);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

async function handleFindNearby() {
    const lng = parseFloat(document.getElementById('nearby-lng').value);
    const lat = parseFloat(document.getElementById('nearby-lat').value);
    const radius = parseFloat(document.getElementById('nearby-radius').value);
    const limitInput = document.getElementById('nearby-limit');
    const limit = limitInput ? parseInt(limitInput.value || '500', 10) : 500;
    const categoryEl = document.getElementById('nearby-category');
    const category = categoryEl && categoryEl.value ? categoryEl.value : '';
    
    if (isNaN(lng) || isNaN(lat)) {
        showToast('Please enter valid coordinates', 'warning');
        return;
    }
    
    try {
        // Backend expects radius (km) as 'radius' and supports optional 'limit' and 'category'
        const params = new URLSearchParams({
            lng: String(lng),
            lat: String(lat),
            radius: String(radius),
            limit: String(limit)
        });
        if (category) params.set('category', category);
        const response = await fetch(`/api/events/nearby?${params.toString()}`);
        const data = await response.json();
        
        displayNearbyEvents(data.features);
        updateMapWithEvents(data.features, [lat, lng]);
    } catch (error) {
        console.error('Error finding nearby events:', error);
        document.getElementById('nearby-events-list').innerHTML = '<p class="text-danger">Error finding nearby events</p>';
    }
}

function displayNearbyEvents(events) {
    const container = document.getElementById('nearby-events-list');
    const countElement = document.getElementById('nearby-events-count');
    
    // Update results count
    if (countElement) {
        countElement.textContent = `${events.length} result${events.length !== 1 ? 's' : ''}`;
        countElement.className = events.length > 0 ? 'badge bg-success' : 'badge bg-secondary';
    }
    
    if (events.length === 0) {
        container.innerHTML = '<div class="p-3"><p class="text-muted">No events found nearby</p></div>';
        return;
    }
    
    const html = events.map((event, index) => {
        const { title, description = '', category, start_date, distance } = event.properties || {};
        const km = typeof distance === 'number' ? (distance / 1000).toFixed(2) : '—';
        const dateStr = start_date ? new Date(start_date).toLocaleString() : '—';
        
        return `
        <div class="border-bottom p-3 nearby-event-item" onclick="centerMapOnEvent(${event.geometry.coordinates[1]}, ${event.geometry.coordinates[0]})" style="cursor: pointer; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#f8f9fa'" onmouseout="this.style.backgroundColor=''">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1 text-primary">${title || 'Untitled Event'}</h6>
                    <p class="mb-2 text-muted small">${description || 'No description available'}</p>
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">
                                <strong>Category:</strong> ${category || '—'}<br>
                                <strong>Date:</strong> ${dateStr}
                            </small>
                        </div>
                        <div class="col-6 text-end">
                            <small class="text-info">
                                <strong>Distance:</strong> ${km} km<br>
                                <strong>#${index + 1}</strong>
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    }).join('');
    
    container.innerHTML = html;
}

function updateMapWithEvents(events, center) {
    if (!map) return;
    
    // Clear existing layer/markers
    if (eventsLayer) {
        map.removeLayer(eventsLayer);
        eventsLayer = null;
    }
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    
    // Center map on search location
    map.setView(center, 12);
    
    // Add marker for search center
    const centerMarker = L.marker(center).addTo(map);
    centerMarker.bindPopup('Search Center').openPopup();
    markers.push(centerMarker);
    
    // Draw GeoJSON features
    eventsLayer = L.geoJSON({ type: 'FeatureCollection', features: events }, {
        pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
            radius: 7,
            fillOpacity: 0.9,
            color: '#333',
            weight: 1,
            fillColor: '#3fb1ce'
        }).bindPopup(`
            <strong>${feature.properties.title}</strong><br>
            ${feature.properties.category || ''}<br>
            ${feature.properties.start_date ? new Date(feature.properties.start_date).toLocaleString() : ''}<br>
            ${typeof feature.properties.distance === 'number' ? `Distance: ${(feature.properties.distance/1000).toFixed(2)} km` : ''}
        `)
    }).addTo(map);
}

function centerMapOnEvent(lat, lng) {
    if (map) {
        map.setView([lat, lng], 15);
    }
}

function handleUseCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                document.getElementById('nearby-lat').value = position.coords.latitude.toFixed(6);
                document.getElementById('nearby-lng').value = position.coords.longitude.toFixed(6);
                showToast('Location updated', 'success');
            },
            (error) => {
                showToast('Unable to get current location', 'error');
            }
        );
    } else {
        showToast('Geolocation not supported', 'error');
    }
}

function updateRadiusDisplay() {
    const radius = document.getElementById('nearby-radius').value;
    document.getElementById('radius-value').textContent = `${radius}km`;
}

// Realtime (EVE-19): basic Socket.IO client that listens for event changes
function initializeRealtime() {
    if (typeof io === 'undefined') return; // Socket.IO not loaded
    try {
        socket = io('/events');
        socket.on('connect', () => {
            showToast('Realtime connected', 'success');
        });
        socket.on('event_created', (payload) => {
            showToast(`Event created: ${payload.event.title}`, 'info');
        });
        socket.on('event_updated', (payload) => {
            showToast(`Event updated: ${payload.event.title}`, 'info');
        });
        socket.on('event_deleted', (payload) => {
            showToast(`Event deleted`, 'warning');
        });
    } catch (e) {
        console.warn('Realtime init failed:', e);
    }
}

// Analytics Functions
async function loadTopVenues() {
    try {
        const response = await fetch('/analytics/top-venues?limit=5');
        const data = await response.json();
        
        displayTopVenues(data.top_venues);
    } catch (error) {
        console.error('Error loading top venues:', error);
        document.getElementById('top-venues-list').innerHTML = '<p class="text-danger">Error loading data</p>';
    }
}

function displayTopVenues(venues) {
    const container = document.getElementById('top-venues-list');
    
    const html = venues.map((venue, index) => `
        <div class="analytics-item">
            <div>
                <div class="analytics-label">${index + 1}. ${venue.venue_name}</div>
                <div class="analytics-value">${venue.venue_address}</div>
            </div>
            <div class="analytics-value">${venue.event_count} events</div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

async function loadSalesData() {
    try {
        const response = await fetch('/analytics/sales-by-month');
        const data = await response.json();
        
        displaySalesData(data.sales_by_month);
    } catch (error) {
        console.error('Error loading sales data:', error);
        document.getElementById('sales-data').innerHTML = '<p class="text-danger">Error loading data</p>';
    }
}

function displaySalesData(sales) {
    const container = document.getElementById('sales-data');
    
    const html = sales.map(sale => `
        <div class="analytics-item">
            <div class="analytics-label">${sale.month}</div>
            <div class="analytics-value">
                $${sale.total_sales.toFixed(2)} (${sale.ticket_count} tickets)
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

async function loadGeneralStats() {
    try {
        const response = await fetch('/analytics/event-stats');
        const data = await response.json();
        
        displayGeneralStats(data);
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('general-stats').innerHTML = '<p class="text-danger">Error loading data</p>';
    }
}

function displayGeneralStats(stats) {
    const container = document.getElementById('general-stats');
    
    const html = `
        <div class="row">
            <div class="col-md-3">
                <div class="performance-metric">
                    <div class="performance-metric-label">Total Events</div>
                    <div class="performance-metric-value">${stats.total_events}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="performance-metric">
                    <div class="performance-metric-label">Total Venues</div>
                    <div class="performance-metric-value">${stats.total_venues}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="performance-metric">
                    <div class="performance-metric-label">Total Users</div>
                    <div class="performance-metric-value">${stats.total_users}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="performance-metric">
                    <div class="performance-metric-label">Total Revenue</div>
                    <div class="performance-metric-value">$${stats.total_revenue.toFixed(2)}</div>
                </div>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-md-4">
                <div class="performance-metric">
                    <div class="performance-metric-label">Active Tickets</div>
                    <div class="performance-metric-value">${stats.ticket_status.active}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="performance-metric">
                    <div class="performance-metric-label">Used Tickets</div>
                    <div class="performance-metric-value">${stats.ticket_status.used}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="performance-metric">
                    <div class="performance-metric-label">Upcoming Events</div>
                    <div class="performance-metric-value">${stats.upcoming_events}</div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Performance Functions
async function explainQuery() {
    const queryId = document.getElementById('query-select').value;
    
    if (!queryId) {
        showToast('Please select a query', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/admin/explain', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query_id: queryId })
        });
        
        const data = await response.json();
        displayQueryResults(data);
    } catch (error) {
        console.error('Error explaining query:', error);
        document.getElementById('query-results').innerHTML = '<p class="text-danger">Error explaining query</p>';
    }
}

function displayQueryResults(data) {
    const container = document.getElementById('query-results');
    
    const explain = data.explain;
    const executionStats = explain.executionStats || explain;
    
    const html = `
        <div class="performance-metric">
            <div class="performance-metric-label">Execution Time</div>
            <div class="performance-metric-value">${executionStats.executionTimeMillis}ms</div>
        </div>
        <div class="performance-metric">
            <div class="performance-metric-label">Documents Examined</div>
            <div class="performance-metric-value">${executionStats.totalDocsExamined}</div>
        </div>
        <div class="performance-metric">
            <div class="performance-metric-label">Index Keys Examined</div>
            <div class="performance-metric-value">${executionStats.totalKeysExamined}</div>
        </div>
        <div class="performance-metric">
            <div class="performance-metric-label">Documents Returned</div>
            <div class="performance-metric-value">${executionStats.nReturned}</div>
        </div>
    `;
    
    container.innerHTML = html;
}

async function loadIndexes() {
    try {
        const response = await fetch('/admin/indexes');
        const data = await response.json();
        
        displayIndexes(data.indexes);
    } catch (error) {
        console.error('Error loading indexes:', error);
        document.getElementById('indexes-info').innerHTML = '<p class="text-danger">Error loading indexes</p>';
    }
}

function displayIndexes(indexes) {
    const container = document.getElementById('indexes-info');
    
    let html = '';
    
    Object.entries(indexes).forEach(([collection, collectionIndexes]) => {
        html += `<h6>${collection}</h6>`;
        collectionIndexes.forEach(index => {
            html += `
                <div class="index-info">
                    <div class="index-name">${index.name}</div>
                    <div class="index-details">
                        Keys: ${JSON.stringify(index.key)}<br>
                        Unique: ${index.unique ? 'Yes' : 'No'}<br>
                        Sparse: ${index.sparse ? 'Yes' : 'No'}
                    </div>
                </div>
            `;
        });
    });
    
    container.innerHTML = html;
}

// Transaction Functions
async function loadEventsForTickets() {
    try {
        const response = await fetch('/events/');
        const data = await response.json();
        
        const select = document.getElementById('ticket-event');
        select.innerHTML = '<option value="">Choose an event...</option>';
        
        data.events.forEach(event => {
            const option = document.createElement('option');
            option.value = event._id;
            option.textContent = `${event.title} - ${new Date(event.datetime).toLocaleDateString()}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading events for tickets:', error);
    }
}

async function loadUsersForTickets() {
    try {
        const response = await fetch('/users/');
        const data = await response.json();
        
        const select = document.getElementById('ticket-user');
        select.innerHTML = '<option value="">Choose a user...</option>';
        
        data.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user._id;
            option.textContent = `${user.name} (${user.email})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading users for tickets:', error);
    }
}

async function buyTicket() {
    const eventId = document.getElementById('ticket-event').value;
    const userId = document.getElementById('ticket-user').value;
    
    if (!eventId || !userId) {
        showToast('Please select both event and user', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/tickets/buy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                eventId: eventId,
                userId: userId
            })
        });
        
        const data = await response.json();
        displayTicketResult(data);
    } catch (error) {
        console.error('Error buying ticket:', error);
        displayTicketResult({ success: false, error: error.message });
    }
}

function displayTicketResult(result) {
    const container = document.getElementById('ticket-result');
    
    if (result.success) {
        container.innerHTML = `
            <div class="ticket-result ticket-success">
                <h6>Ticket Purchased Successfully!</h6>
                <p><strong>Ticket ID:</strong> ${result.ticket_id}</p>
                <p><strong>Event:</strong> ${result.event_title}</p>
                <p><strong>Seats Remaining:</strong> ${result.seats_remaining}</p>
                <p><strong>Price Paid:</strong> $${result.price_paid}</p>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="ticket-result ticket-error">
                <h6>Purchase Failed</h6>
                <p>${result.error}</p>
            </div>
        `;
    }
}

async function runTransactionDemo() {
    try {
        const response = await fetch('/db/transactions_demo.py');
        // This would need to be implemented as an API endpoint
        showToast('Transaction demo would run here', 'info');
    } catch (error) {
        console.error('Error running transaction demo:', error);
        showToast('Error running transaction demo', 'error');
    }
}

// Utility Functions
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to container
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}
