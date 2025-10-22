# Distributed Database Management System - Quick Start

## Setup Instructions

### 1. Install Dependencies

```powershell
# Navigate to project directory
cd path\to\DistributedDatabaseManagementSystem

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Databases

#### PostgreSQL Setup

For local development, you can use a single PostgreSQL instance with multiple databases to simulate sharding:

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create databases for each shard
CREATE DATABASE elearning_na;
CREATE DATABASE elearning_eu;
CREATE DATABASE elearning_asia;
```

**Note**: For a true distributed setup, configure separate PostgreSQL instances on different ports.

#### MongoDB Setup

```powershell
# Start MongoDB
mongod --dbpath C:\data\db

# Or use MongoDB Compass for GUI management
```

### 3. Configure Environment

```powershell
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# For local setup, default values should work
```

### 4. Initialize Databases

```powershell
# Run setup script
python db/setup_database.py
```

This will:
- Create all PostgreSQL databases
- Load schemas and stored procedures
- Create MongoDB collections
- Set up indexes

### 5. Populate Sample Data

```powershell
# Generate sample data
python db/sample_data_generator.py
```

This creates:
- 100 students
- 20 instructors
- 50 courses with modules and lessons
- 200 enrollments with progress
- 150 transactions

### 6. Verify Installation

```powershell
# Run health check
python db/health_check.py
```

Expected output:
```
✓ PostgreSQL: 6/6 nodes healthy
✓ MongoDB: HEALTHY
✓ Sample data loaded
```

## Project Structure

```
DistributedDatabaseManagementSystem/
├── db/
│   ├── config/
│   │   └── database_config.py          # Database configuration
│   ├── postgres_scripts/
│   │   ├── schema.sql                   # PostgreSQL schema
│   │   ├── stored_procedures.sql        # Stored procedures
│   │   ├── connection_manager.py        # Connection pooling
│   │   ├── user_crud.py                 # User operations
│   │   ├── course_crud.py               # Course operations
│   │   ├── enrollment_crud.py           # Enrollment operations
│   │   └── payment_crud.py              # Payment operations
│   ├── mongo_scripts/
│   │   └── connection_manager.py        # MongoDB manager
│   ├── setup_database.py                # Database initialization
│   ├── sample_data_generator.py         # Sample data generator
│   ├── health_check.py                  # Health monitoring
│   └── DATABASE_GUIDE.md                # Complete documentation
├── requirements.txt                      # Python dependencies
├── .env.example                         # Environment template
└── README.md                            # Project overview
```

## Quick Usage Examples

### Example 1: Create a User

```python
from db.postgres_scripts.user_crud import UserCRUD

user_crud = UserCRUD()

user_id = user_crud.create_user(
    email="student@example.com",
    password="securepass123",
    first_name="Jane",
    last_name="Doe",
    user_type="student",
    region="north_america"
)

print(f"Created user: {user_id}")
```

### Example 2: Create and Publish a Course

```python
from db.postgres_scripts.course_crud import CourseCRUD

course_crud = CourseCRUD()

# Create course
course_id = course_crud.create_course(
    course_code="PY101",
    title="Python Fundamentals",
    description="Learn Python basics",
    instructor_id=instructor_id,
    region="north_america",
    level="beginner",
    price=49.99
)

# Publish course
course_crud.publish_course(course_id, "north_america")
```

### Example 3: Enroll and Track Progress

```python
from db.postgres_scripts.enrollment_crud import EnrollmentCRUD

enrollment_crud = EnrollmentCRUD()

# Enroll student
enrollment_id = enrollment_crud.enroll_user(
    user_id=student_id,
    course_id=course_id,
    region="north_america"
)

# Mark lesson complete
enrollment_crud.mark_lesson_complete(
    enrollment_id=enrollment_id,
    lesson_id=lesson_id,
    region="north_america",
    time_spent=20
)
```

## Key Features

✓ **Master-Slave Replication**: Write to master, read from slaves  
✓ **Horizontal Sharding**: Data partitioned by geographic region  
✓ **Connection Pooling**: Efficient resource management  
✓ **3NF Normalized Schema**: Optimized data integrity  
✓ **Stored Procedures**: Complex operations at DB level  
✓ **Automatic Triggers**: Progress tracking, rating updates  
✓ **MongoDB Integration**: Unstructured content storage  
✓ **CRUD Operations**: Complete data access layer  

## Database Sharding Map

| Region | Shard ID | Master Port | Slave Port | Database |
|--------|----------|-------------|------------|----------|
| North America | 1 | 5432 | 5435 | elearning_na |
| Europe | 2 | 5433 | 5436 | elearning_eu |
| Asia | 3 | 5434 | 5437 | elearning_asia |

## Next Steps

1. **Explore the API**: Integrate with the RESTful API layer
2. **Add Business Logic**: Implement additional services
3. **Configure Networking**: Set up TCP/UDP communication
4. **Add Monitoring**: Implement comprehensive logging
5. **Scale**: Add more shards or replicas as needed

## Common Commands

```powershell
# Activate environment
.\venv\Scripts\activate

# Check health
python db/health_check.py

# Regenerate data
python db/sample_data_generator.py

# Run tests (if available)
pytest tests/

# Deactivate environment
deactivate
```

## Troubleshooting

**Issue**: Cannot connect to PostgreSQL  
**Solution**: Ensure PostgreSQL is running and credentials in `.env` are correct

**Issue**: MongoDB connection refused  
**Solution**: Start MongoDB service: `net start MongoDB`

**Issue**: Import errors  
**Solution**: Ensure virtual environment is activated and dependencies installed

## Documentation

- **Complete Guide**: See `db/DATABASE_GUIDE.md`
- **Schema Details**: See `db/postgres_scripts/schema.sql`
- **API Reference**: See stored procedures documentation

## Support

For detailed information, refer to:
- `DATABASE_GUIDE.md` - Comprehensive documentation
- `schema.sql` - Database schema details
- `stored_procedures.sql` - Available procedures

---

**Ready to start building!** 🚀
