# Database Layer - Complete Guide

## Overview

This database layer implements a **distributed database management system** for a global e-learning platform with:

- **PostgreSQL**: Master-slave replication with horizontal sharding by region
- **MongoDB**: Unstructured content storage (videos, documents, user preferences)
- **Connection Pooling**: Efficient resource management
- **3NF Normalized Schema**: Optimized for data integrity
- **CRUD Operations**: Complete data access layer
- **Stored Procedures & Triggers**: Business logic at database level

---

## Architecture

### PostgreSQL Sharding Strategy

The system uses **horizontal partitioning** based on geographic regions:

```
Shard 1 (North America): 
  - Master: localhost:5432
  - Slave:  localhost:5435

Shard 2 (Europe):
  - Master: localhost:5433
  - Slave:  localhost:5436

Shard 3 (Asia):
  - Master: localhost:5434
  - Slave:  localhost:5437
```

**Region Mapping:**
- `north_america`, `south_america` → Shard 1
- `europe`, `africa` → Shard 2
- `asia`, `oceania` → Shard 3

### Master-Slave Replication

- **Write operations** go to **master nodes**
- **Read operations** can use **slave nodes** (load balancing)
- Automatic failover can be configured for high availability

---

## Installation

### Prerequisites

1. **PostgreSQL 12+** installed
2. **MongoDB 4.4+** installed
3. **Python 3.10+**

### Setup Steps

```powershell
```powershell
# 1. Navigate to project directory
cd path\to\DistributedDatabaseManagementSystem

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# 5. Initialize databases
python db/setup_database.py

# 6. Populate with sample data
python db/sample_data_generator.py

# 7. Run health check
python db/health_check.py
```

---

## Database Schema

### PostgreSQL Tables

#### Users & Profiles
- **users**: Core user information (normalized)
- **user_profiles**: Extended profile data (1:1 relationship)

#### Courses
- **course_categories**: Course categorization
- **courses**: Course metadata
- **course_modules**: Course sections
- **course_lessons**: Individual lessons

#### Enrollments
- **enrollments**: User course enrollments
- **lesson_progress**: Detailed progress tracking
- **course_reviews**: User reviews and ratings

#### Payments
- **payment_methods**: Stored payment information
- **transactions**: Payment transactions
- **invoices**: Generated invoices

### MongoDB Collections

#### course_content
Stores multimedia content:
```json
{
  "content_id": "uuid",
  "course_id": "uuid",
  "lesson_id": "uuid",
  "content_type": "video|document|quiz",
  "video_url": "https://...",
  "duration_seconds": 1200,
  "thumbnail_url": "https://...",
  "views": 0
}
```

#### user_preferences
Stores user preferences:
```json
{
  "user_id": "uuid",
  "preferences": {
    "learning": {
      "preferred_categories": ["programming", "data_science"],
      "difficulty_level": "intermediate"
    },
    "notifications": {
      "email": true,
      "push": false
    },
    "wishlist": ["course_id_1", "course_id_2"],
    "recently_viewed": []
  }
}
```

---

## Usage Examples

### 1. User Management

```python
from db.postgres_scripts.user_crud import UserCRUD

user_crud = UserCRUD()

# Create a new user
user_id = user_crud.create_user(
    email="john.doe@example.com",
    password="secure_password",
    first_name="John",
    last_name="Doe",
    user_type="student",
    region="north_america",
    country="United States",
    city="New York"
)

# Get user by email
user = user_crud.get_user_by_email(
    email="john.doe@example.com",
    region="north_america"
)

# Update user profile
user_crud.update_user_profile(
    user_id=user_id,
    region="north_america",
    profile_data={
        "bio": "Passionate learner",
        "timezone": "America/New_York"
    }
)

# Authenticate user
user = user_crud.authenticate_user(
    email="john.doe@example.com",
    password="secure_password",
    region="north_america"
)
```

### 2. Course Management

```python
from db.postgres_scripts.course_crud import CourseCRUD

course_crud = CourseCRUD()

# Create a course
course_id = course_crud.create_course(
    course_code="PYTHON-101",
    title="Python for Beginners",
    description="Learn Python programming from scratch",
    instructor_id=instructor_id,
    region="north_america",
    level="beginner",
    price=49.99,
    duration_hours=20
)

# Add modules and lessons
module_id = course_crud.create_course_module(
    course_id=course_id,
    region="north_america",
    module_title="Introduction to Python",
    module_order=1
)

lesson_id = course_crud.create_course_lesson(
    module_id=module_id,
    region="north_america",
    lesson_title="Variables and Data Types",
    lesson_order=1,
    lesson_type="video",
    content_id="content_123",
    duration_minutes=15
)

# Publish course
course_crud.publish_course(course_id, "north_america")

# Search courses
courses = course_crud.search_courses(
    region="north_america",
    search_term="Python",
    min_rating=4.0
)
```

### 3. Enrollment & Progress

```python
from db.postgres_scripts.enrollment_crud import EnrollmentCRUD

enrollment_crud = EnrollmentCRUD()

# Enroll user in course
enrollment_id = enrollment_crud.enroll_user(
    user_id=user_id,
    course_id=course_id,
    region="north_america"
)

# Mark lesson complete
enrollment_crud.mark_lesson_complete(
    enrollment_id=enrollment_id,
    lesson_id=lesson_id,
    region="north_america",
    time_spent=15
)

# Get course progress
progress = enrollment_crud.get_course_progress(
    enrollment_id=enrollment_id,
    region="north_america"
)

# Add review
enrollment_crud.add_course_review(
    enrollment_id=enrollment_id,
    region="north_america",
    rating=5,
    review_text="Excellent course!"
)
```

### 4. Payment Processing

```python
from db.postgres_scripts.payment_crud import PaymentCRUD

payment_crud = PaymentCRUD()

# Add payment method
payment_method_id = payment_crud.add_payment_method(
    user_id=user_id,
    region="north_america",
    method_type="credit_card",
    card_last_four="4242",
    card_brand="Visa",
    expiry_month=12,
    expiry_year=2025,
    is_default=True
)

# Create transaction
transaction_id = payment_crud.create_transaction(
    user_id=user_id,
    course_id=course_id,
    region="north_america",
    amount=49.99,
    payment_method_id=payment_method_id
)

# Complete transaction
invoice_id = payment_crud.complete_transaction(
    transaction_id=transaction_id,
    region="north_america",
    gateway_transaction_id="stripe_ch_123456"
)

# Get transaction history
transactions = payment_crud.get_user_transactions(
    user_id=user_id,
    region="north_america",
    limit=10
)
```

### 5. MongoDB Content Management

```python
from db.mongo_scripts.connection_manager import (
    get_mongo_manager,
    CourseContentManager,
    UserPreferencesManager
)

mongo_manager = get_mongo_manager()
content_manager = CourseContentManager(mongo_manager)
preferences_manager = UserPreferencesManager(mongo_manager)

# Add video content
content_manager.add_video_content(
    content_id="content_123",
    course_id=course_id,
    lesson_id=lesson_id,
    title="Introduction Video",
    video_url="https://videos.example.com/intro.mp4",
    duration_seconds=900,
    thumbnail_url="https://images.example.com/thumb.jpg"
)

# Add document content
content_manager.add_document_content(
    content_id="content_124",
    course_id=course_id,
    lesson_id=lesson_id,
    title="Course Notes",
    document_url="https://docs.example.com/notes.pdf",
    document_type="pdf",
    file_size_bytes=1024000,
    page_count=50
)

# Set user preferences
preferences_manager.set_learning_preferences(
    user_id=user_id,
    preferred_categories=["programming", "data_science"],
    preferred_languages=["English"],
    difficulty_level="intermediate",
    learning_pace="moderate"
)

# Add to wishlist
preferences_manager.add_to_wishlist(user_id, course_id)
```

---

## Stored Procedures

### User Management
- `create_user_with_profile()`: Create user with profile
- `get_user_by_email()`: Retrieve user by email
- `update_user_login()`: Update last login timestamp

### Course Management
- `create_course()`: Create new course
- `get_course_details()`: Get detailed course info
- `get_popular_courses()`: Get trending courses
- `search_courses()`: Search with filters

### Enrollment
- `enroll_user()`: Enroll user in course
- `get_user_enrollments()`: Get user's enrollments
- `mark_lesson_complete()`: Mark lesson as complete
- `get_course_progress()`: Get detailed progress

### Payments
- `create_transaction()`: Create payment transaction
- `complete_transaction()`: Complete and generate invoice
- `get_user_transactions()`: Get transaction history

### Analytics
- `get_instructor_stats()`: Instructor statistics
- `get_platform_stats()`: Platform-wide statistics

---

## Triggers

### Automatic Updates
- **update_modified_timestamp**: Auto-update `updated_at` on record changes
- **update_course_rating**: Recalculate course rating on new reviews
- **update_enrollment_progress**: Update enrollment progress on lesson completion

---

## Connection Management

### Connection Pooling

The system uses connection pooling for optimal performance:

```python
from db.postgres_scripts.connection_manager import get_postgres_manager

pg_manager = get_postgres_manager()

# Execute query with automatic connection management
result = pg_manager.execute_query(
    region="north_america",
    query="SELECT * FROM users WHERE user_id = %s",
    params=(user_id,),
    read_only=True
)

# Close all connections when done
pg_manager.close_all_connections()
```

### Master-Slave Selection

```python
# Read from slave (load balancing)
result = pg_manager.execute_query(
    region="north_america",
    query="SELECT * FROM courses",
    read_only=True  # Uses slave node
)

# Write to master
pg_manager.execute_query(
    region="north_america",
    query="INSERT INTO users (...) VALUES (...)",
    read_only=False  # Uses master node
)
```

---

## Performance Optimization

### Indexes

All tables have appropriate indexes on:
- Primary keys (automatic)
- Foreign keys
- Frequently queried columns
- Composite indexes for common query patterns

### Query Optimization

- Use stored procedures for complex operations
- Leverage read replicas for heavy read workloads
- Connection pooling reduces overhead
- Prepared statements prevent SQL injection

---

## Monitoring & Health Checks

```powershell
# Run health check
python db/health_check.py
```

Output includes:
- PostgreSQL node health (all masters and slaves)
- MongoDB connection status
- Database statistics
- Error reporting

---

## Scaling Considerations

### Horizontal Scaling
- Add more shards for new regions
- Add more slave nodes per shard for read scaling
- Implement connection pooling at application level

### Vertical Scaling
- Increase connection pool sizes
- Optimize query performance
- Add indexes for new query patterns

### Future Enhancements
- Implement automatic failover
- Add caching layer (Redis)
- Implement distributed transactions
- Add data replication monitoring

---

## Security Best Practices

1. **Password Hashing**: All passwords are hashed using SHA-256
2. **Parameterized Queries**: Prevents SQL injection
3. **Connection Encryption**: Use SSL/TLS in production
4. **Environment Variables**: Store credentials securely
5. **Role-Based Access**: Implement database roles and permissions

---

## Troubleshooting

### Connection Issues

```python
# Check database health
from db.health_check import DatabaseHealthCheck

health = DatabaseHealthCheck()
health.run_full_check()
```

### Common Errors

**"Unknown region"**: Ensure region is in the REGION_MAPPING
**"Connection refused"**: Check PostgreSQL/MongoDB is running
**"Pool exhausted"**: Increase pool size in configuration

---

## Testing

```powershell
# Run tests (if implemented)
pytest tests/

# Manual testing with sample data
python db/sample_data_generator.py
```

---

## Maintenance

### Backup
```sql
-- PostgreSQL backup
pg_dump -h localhost -p 5432 -U postgres elearning_na > backup.sql

-- MongoDB backup
mongodump --db elearning_content --out backup/
```

### Restore
```sql
-- PostgreSQL restore
psql -h localhost -p 5432 -U postgres elearning_na < backup.sql

-- MongoDB restore
mongorestore --db elearning_content backup/elearning_content
```

---

## Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Run health check utility
4. Review database configuration

---

**Last Updated**: October 2025  
**Version**: 1.0.0
