# MongoDB Atlas Setup Guide for Enhanced Check-ins Testing

## Overview
This guide explains how to set up and test the enhanced check-ins functionality with MongoDB Atlas, including environment configuration for different locations (home, school, laptop).

## Prerequisites
- Python 3.8+ with virtual environment
- MongoDB Atlas account with EventSphere project
- Network access configured for your IP addresses

## MongoDB Atlas Configuration

### 1. Atlas Project Details
- **Project Name**: EventSphere
- **Cluster**: eventsphere.mzturli.mongodb.net
- **Database**: EventSphere
- **Username**: chrislawrencedev
- **Password**: `password`

### 2. Connection String
```
mongodb+srv://chrislawrencedev:<password>@eventsphere.mzturli.mongodb.net/EventSphere?retryWrites=true&w=majority&appName=EventSphere
```

### 3. Network Access Setup
You need to add your current IP address to the Atlas Network Access list:

1. Go to [MongoDB Atlas Dashboard](https://cloud.mongodb.com)
2. Navigate to **Security** → **Network Access**
3. Click **Add IP Address**
4. Add your current IP address (you can get it from [whatismyipaddress.com](https://whatismyipaddress.com))
5. Click **Confirm**

**Important**: You'll need to do this for each location:
- Home IP address
- School IP address  
- Laptop IP address (if different)

## Environment Setup

### 1. Clone and Setup Repository
```bash
git clone <your-repo-url>
cd mongo-events-demo
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create or update `.env` file in the project root:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://chrislawrencedev:<password>@eventsphere.mzturli.mongodb.net/EventSphere?retryWrites=true&w=majority&appName=EventSphere
MONGODB_DB_NAME=EventSphere
MONGODB_ATLAS_USERNAME=chrislawrencedev
MONGODB_ATLAS_PASSWORD=Xc93FPujnvVD2Xb6

# Database Type (use 'cloud' for Atlas)
DB_TYPE=cloud

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Application Settings
HOST=127.0.0.1
PORT=5001
```

### 3. Verify Connection
Test the Atlas connection:
```bash
cd /path/to/mongo-events-demo
source .venv/bin/activate
python test_simple_atlas.py
```

Expected output:
```
🔌 Testing MongoDB Atlas Connection...
✅ Successfully connected to MongoDB Atlas!
📁 Available collections: ['events', 'checkins', 'venues', 'users']
🎉 MongoDB Atlas connection test successful!
```

## Testing Enhanced Check-ins

### 1. Run Unit Tests (No Database Required)
```bash
python test_checkins_standalone.py
```

### 2. Run Integration Tests (Requires Atlas Connection)
```bash
python -m pytest tests/test_enhanced_checkins.py -v
```

### 3. Start the Application
```bash
python run.py
```

The application will be available at `http://localhost:5001`

### 4. Test API Endpoints

#### Create a Check-in
```bash
curl -X POST http://localhost:5001/api/checkins \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "507f1f77bcf86cd799439011",
    "user_id": "507f1f77bcf86cd799439012",
    "venue_id": "507f1f77bcf86cd799439013",
    "qr_code": "QR123456789",
    "ticket_tier": "VIP",
    "check_in_method": "qr_code",
    "metadata": {
      "device_info": "iPhone 13 Pro",
      "ip_address": "192.168.1.100",
      "staff_verified": true
    }
  }'
```

#### Get Analytics
```bash
# Get repeat attendees
curl http://localhost:5001/api/checkins/analytics/repeat-attendees

# Get time patterns
curl http://localhost:5001/api/checkins/analytics/time-patterns

# Get venue statistics
curl http://localhost:5001/api/checkins/analytics/venue/507f1f77bcf86cd799439013
```

## Location-Specific Setup

### Home Setup
1. Get your home IP address
2. Add it to Atlas Network Access
3. Update `.env` if needed
4. Run tests

### School Setup
1. Get your school IP address
2. Add it to Atlas Network Access
3. Update `.env` if needed
4. Run tests

### Laptop Setup
1. Get your laptop's current IP address
2. Add it to Atlas Network Access
3. Update `.env` if needed
4. Run tests

## Troubleshooting

### Connection Issues
1. **"Connection refused"**: Check if your IP is added to Network Access
2. **"Authentication failed"**: Verify username/password in `.env`
3. **"Timeout"**: Check internet connection and firewall settings

### Schema Validation Issues
1. **"Document failed validation"**: The enhanced schema is working correctly
2. **"Required field missing"**: Ensure all required fields are provided
3. **"Invalid ObjectId"**: Use proper ObjectId format for IDs

### Environment Issues
1. **"Module not found"**: Ensure virtual environment is activated
2. **"Permission denied"**: Check file permissions and ownership
3. **"Command not found"**: Ensure Python and pip are in PATH

## MongoDB Shell (Optional)

If you want to interact with the database directly:

### Install mongosh
```bash
# Download from MongoDB website
wget https://downloads.mongodb.com/compass/mongodb-mongosh_2.5.8_amd64.deb
sudo dpkg -i mongodb-mongosh_2.5.8_amd64.deb
```

### Connect to Atlas
```bash
mongosh "mongodb+srv://chrislawrencedev:<password>@eventsphere.mzturli.mongodb.net/EventSphere?retryWrites=true&w=majority"
```

### Useful Commands
```javascript
// List collections
show collections

// Count documents
db.checkins.countDocuments({})

// Find sample documents
db.checkins.find().limit(5)

// Check indexes
db.checkins.getIndexes()

// View schema validation
db.runCommand({listCollections: 1, filter: {name: "checkins"}})
```

## Enhanced Check-ins Features

### Schema Features
- **venue_id denormalization** for analytics performance
- **check_in_method** tracking (qr_code, manual, mobile_app)
- **metadata** for device info, IP address, staff verification
- **created_at** timestamp for record tracking

### Analytics Capabilities
- Event attendance statistics
- Venue analytics with monthly breakdowns
- Repeat attendees identification
- Check-in time pattern analysis
- User attendance history

### API Endpoints
- `POST /api/checkins` - Create check-in with duplicate prevention
- `GET /api/checkins/analytics/*` - Various analytics endpoints
- `GET /api/checkins/event/<id>` - Event check-ins
- `GET /api/checkins/user/<id>` - User check-ins
- `GET /api/checkins/venue/<id>` - Venue check-ins

## Performance Expectations

With MongoDB Atlas:
- **Basic CRUD operations**: < 25ms
- **Analytics aggregations**: < 150ms
- **Duplicate prevention checks**: < 10ms
- **Venue statistics**: < 100ms
- **Repeat attendees analysis**: < 200ms

## Security Notes

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate passwords** regularly
4. **Monitor access logs** in Atlas dashboard
5. **Use least privilege** for database users

## Next Steps

1. Test all enhanced check-ins features
2. Run performance benchmarks
3. Create sample data for testing
4. Document any issues or improvements
5. Prepare for production deployment

---

**Last Updated**: January 2025
**Version**: 1.0
**Status**: Ready for Testing
