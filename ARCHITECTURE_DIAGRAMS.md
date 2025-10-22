# Distributed Database Architecture - Visual Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        E-LEARNING PLATFORM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │  Application     │
                              │  Layer (Future)  │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
         ┌──────────▼──────────┐              ┌─────────▼──────────┐
         │  Connection Manager │              │  Connection Manager │
         │   (PostgreSQL)      │              │    (MongoDB)        │
         └──────────┬──────────┘              └─────────┬──────────┘
                    │                                    │
         ┌──────────┴──────────┐                       │
         │   Region Routing    │                       │
         │   (Sharding Logic)  │                       │
         └──────────┬──────────┘                       │
                    │                                   │
    ┌───────────────┼───────────────┐                 │
    │               │               │                 │
┌───▼────┐    ┌────▼─────┐   ┌────▼─────┐   ┌───────▼────────┐
│ Shard 1│    │ Shard 2  │   │ Shard 3  │   │   MongoDB      │
│N. Amer.│    │  Europe  │   │   Asia   │   │   Cluster      │
└───┬────┘    └────┬─────┘   └────┬─────┘   └────────────────┘
    │              │              │          
    ├─Master       ├─Master       ├─Master   ┌─────────────────┐
    │  (5432)      │  (5433)      │  (5434)  │ course_content  │
    │              │              │          │ user_preferences│
    └─Slave        └─Slave        └─Slave    └─────────────────┘
       (5435)         (5436)         (5437)
```

---

## Data Flow Diagrams

### 1. User Registration Flow (Write Operation)

```
User Registration Request
         │
         ▼
    [User CRUD]
         │
         ├─── Determine Region (north_america)
         │
         ▼
 [Connection Manager]
         │
         ├─── Route to Master Node (Shard 1)
         │
         ▼
  [PostgreSQL Master]
         │
         ├─── Execute: create_user_with_profile()
         │    • Insert into users table
         │    • Insert into user_profiles table
         │    • Trigger: update_modified_timestamp
         │
         ▼
  [Replication to Slave]
         │
         ▼
    [MongoDB - User Preferences]
         │
         ├─── Create user_preferences document
         │
         ▼
    Return User ID
```

### 2. Course Enrollment Flow (Mixed Operations)

```
Enrollment Request
         │
         ▼
 [Enrollment CRUD]
         │
         ├─── Check Course Capacity (Read from Slave)
         │
         ▼
 [PostgreSQL Slave] ───── Read: course.max_enrollments
         │
         ├─── If capacity available
         │
         ▼
 [PostgreSQL Master]
         │
         ├─── Execute: enroll_user()
         │    • Insert into enrollments
         │    • Insert into lesson_progress (bulk)
         │    • Trigger: update_enrollment_progress
         │
         ▼
 [MongoDB - Course Content]
         │
         ├─── Fetch lesson content_ids
         │
         ▼
    Return Enrollment ID + Course Curriculum
```

### 3. Progress Tracking Flow (Automatic Triggers)

```
Mark Lesson Complete
         │
         ▼
 [Enrollment CRUD]
         │
         ├─── mark_lesson_complete()
         │
         ▼
 [PostgreSQL Master]
         │
         ├─── UPDATE lesson_progress
         │    • Set completed = TRUE
         │    • Set completion_date = NOW()
         │    • Add time_spent
         │
         ▼
    [TRIGGER: update_enrollment_progress]
         │
         ├─── Calculate: completed_lessons / total_lessons
         │
         ├─── UPDATE enrollments
         │    • progress_percentage = X%
         │    • status = 'completed' (if 100%)
         │    • completion_date = NOW() (if 100%)
         │
         ▼
    [Replicate to Slaves]
         │
         ▼
    Progress Updated Automatically
```

### 4. Payment Processing Flow (Transactional)

```
Purchase Course
         │
         ▼
  [Payment CRUD]
         │
         ├─── create_transaction()
         │
         ▼
 [PostgreSQL Master] ──── BEGIN TRANSACTION
         │
         ├─── INSERT INTO transactions
         │    • status = 'pending'
         │    • amount, currency, payment_method
         │
         ▼
 [Payment Gateway API] (External - Future)
         │
         ├─── Process Payment
         │
         ▼
  [Payment CRUD]
         │
         ├─── complete_transaction()
         │
         ▼
 [PostgreSQL Master]
         │
         ├─── UPDATE transactions
         │    • status = 'completed'
         │    • gateway_transaction_id
         │
         ├─── Calculate tax (10%)
         │
         ├─── INSERT INTO invoices
         │    • invoice_number (auto-generated)
         │    • subtotal, tax, total
         │    • status = 'paid'
         │
         ├─── COMMIT TRANSACTION
         │
         ▼
    Return Invoice ID
```

---

## Connection Pool Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  Connection Pool Manager                      │
└──────────────────────────────────────────────────────────────┘

    Master Pool (Shard 1)          Slave Pool (Shard 1)
    ┌──────────────────┐           ┌──────────────────┐
    │ ○ ○ ○ ○ ○ ○ ○   │           │ ○ ○ ○ ○ ○ ○ ○   │
    │ Min: 1           │           │ Min: 1           │
    │ Max: 10          │           │ Max: 10          │
    │ Timeout: 30s     │           │ Timeout: 30s     │
    └────────┬─────────┘           └────────┬─────────┘
             │                              │
    ┌────────▼────────┐           ┌────────▼────────┐
    │  Master Node    │           │  Slave Node     │
    │  localhost:5432 │──Repl───▶ │  localhost:5435 │
    └─────────────────┘           └─────────────────┘

Legend:
○ = Available Connection
● = Active Connection
Repl = Replication Stream
```

---

## Sharding Strategy Visualization

```
┌──────────────────────────────────────────────────────────────────┐
│                     GEOGRAPHIC SHARDING MAP                       │
└──────────────────────────────────────────────────────────────────┘

    Incoming Request
          │
          ▼
    [Region Identifier]
          │
          ├─────────────────┬──────────────────┐
          ▼                 ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ SHARD 1  │      │ SHARD 2  │      │ SHARD 3  │
    ├──────────┤      ├──────────┤      ├──────────┤
    │ Regions: │      │ Regions: │      │ Regions: │
    │ • N.Amer.│      │ • Europe │      │ • Asia   │
    │ • S.Amer.│      │ • Africa │      │ • Oceania│
    └──────────┘      └──────────┘      └──────────┘
         │                 │                  │
    ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
    │ Master  │       │ Master  │       │ Master  │
    │ :5432   │       │ :5433   │       │ :5434   │
    └────┬────┘       └────┬────┘       └────┬────┘
         │                 │                  │
    ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
    │ Slave   │       │ Slave   │       │ Slave   │
    │ :5435   │       │ :5436   │       │ :5437   │
    └─────────┘       └─────────┘       └─────────┘

Region-to-Shard Mapping:
• north_america → Shard 1
• south_america → Shard 1
• europe        → Shard 2
• africa        → Shard 2
• asia          → Shard 3
• oceania       → Shard 3
```

---

## Database Schema Entity Relationship

```
┌─────────────────────────────────────────────────────────────────┐
│                        POSTGRESQL SCHEMA                         │
└─────────────────────────────────────────────────────────────────┘

    ┌────────────┐         ┌──────────────┐
    │   users    │◄───1:1──┤user_profiles │
    └──────┬─────┘         └──────────────┘
           │
           │ 1:N (instructor)
           ▼
    ┌────────────┐         ┌──────────────────┐
    │  courses   │◄───N:1──┤course_categories │
    └──────┬─────┘         └──────────────────┘
           │
           │ 1:N
           ▼
    ┌─────────────────┐
    │ course_modules  │
    └────────┬────────┘
             │ 1:N
             ▼
    ┌─────────────────┐    ┌──────────────────┐
    │ course_lessons  │───▶│   MongoDB        │
    └────────┬────────┘    │ course_content   │
             │             └──────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    │  users (N:M via enrollments)
    │                 │
    ▼                 ▼
┌──────────┐    ┌─────────────────┐    ┌───────────────┐
│  users   │───▶│  enrollments    │───▶│course_reviews │
└──────┬───┘    └────────┬────────┘    └───────────────┘
       │                 │
       │                 │ 1:N
       │                 ▼
       │        ┌─────────────────┐
       │        │ lesson_progress │
       │        └─────────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐    ┌────────────────┐
│payment_methods│   │ transactions   │
└──────────────┘    └────────┬───────┘
                             │ 1:1
                             ▼
                    ┌────────────────┐
                    │   invoices     │
                    └────────────────┘
```

---

## MongoDB Collections Structure

```
┌──────────────────────────────────────────────────────────────┐
│                      MONGODB COLLECTIONS                      │
└──────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ course_content                                        │
├───────────────────────────────────────────────────────┤
│ {                                                     │
│   content_id: "uuid",                                 │
│   course_id: "uuid",           ◄─── Links to PG     │
│   lesson_id: "uuid",           ◄─── Links to PG     │
│   content_type: "video|document|quiz",               │
│   video_url: "https://...",                          │
│   document_url: "https://...",                       │
│   duration_seconds: 900,                             │
│   thumbnail_url: "https://...",                      │
│   views: 1234,                                       │
│   quality_options: [...],                            │
│   created_at: ISODate(),                             │
│   updated_at: ISODate()                              │
│ }                                                     │
└───────────────────────────────────────────────────────┘
         │
         │ Indexes:
         ├─── content_id (unique)
         ├─── course_id
         └─── lesson_id

┌───────────────────────────────────────────────────────┐
│ user_preferences                                      │
├───────────────────────────────────────────────────────┤
│ {                                                     │
│   user_id: "uuid",             ◄─── Links to PG     │
│   preferences: {                                     │
│     learning: {                                      │
│       preferred_categories: ["prog", "ds"],         │
│       difficulty_level: "intermediate",             │
│       learning_pace: "moderate"                     │
│     },                                               │
│     notifications: {                                 │
│       email: true,                                   │
│       push: false                                    │
│     },                                               │
│     wishlist: ["course_id_1", ...],                 │
│     recently_viewed: [...]                           │
│   },                                                  │
│   created_at: ISODate(),                             │
│   updated_at: ISODate()                              │
│ }                                                     │
└───────────────────────────────────────────────────────┘
         │
         │ Indexes:
         └─── user_id (unique)
```

---

## Deployment Architecture (Local Simulation)

```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT SETUP                   │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────┐
    │           localhost (127.0.0.1)                 │
    └─────────────────────────────────────────────────┘
              │
    ┌─────────┴───────────────────────┐
    │                                 │
    ▼                                 ▼
┌─────────────────┐         ┌──────────────────┐
│  PostgreSQL     │         │    MongoDB       │
│  Instance       │         │    Instance      │
├─────────────────┤         ├──────────────────┤
│ Port 5432 (M1)  │         │ Port 27017       │
│ Port 5433 (M2)  │         │ Database:        │
│ Port 5434 (M3)  │         │  elearning_      │
│ Port 5435 (S1)  │         │  content         │
│ Port 5436 (S2)  │         └──────────────────┘
│ Port 5437 (S3)  │
│                 │
│ Databases:      │
│ • elearning_na  │
│ • elearning_eu  │
│ • elearning_asia│
└─────────────────┘

Legend:
M = Master Node
S = Slave Node
```

---

## Query Execution Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    QUERY EXECUTION PATH                       │
└──────────────────────────────────────────────────────────────┘

Python Application
      │
      ▼
[CRUD Layer]
      │
      ├─── user_crud.get_user_by_email()
      │
      ▼
[Connection Manager]
      │
      ├─── Region: north_america
      ├─── Read Only: True
      │
      ▼
[Connection Pool]
      │
      ├─── Get connection from Slave Pool (Shard 1)
      │
      ▼
[PostgreSQL Slave]
      │
      ├─── Execute: SELECT * FROM users WHERE email = %s
      ├─── Use Index: idx_users_email
      ├─── Join: user_profiles
      │
      ▼
[Result Set] ──── RealDictCursor ────▶ Python Dict
      │
      ▼
[Connection Pool]
      │
      ├─── Return connection to pool
      │
      ▼
Return Result to Application
```

---

## Monitoring & Health Check Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      HEALTH CHECK SYSTEM                      │
└──────────────────────────────────────────────────────────────┘

    [health_check.py]
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
[PostgreSQL] [MongoDB]
    │             │
    ├─Check       ├─Ping
    │ Master 1    │ Primary
    ├─Check       └─────┬─────▶ Status
    │ Slave 1            │
    ├─Check              ▼
    │ Master 2     ┌─────────────┐
    ├─Check        │   Report    │
    │ Slave 2      ├─────────────┤
    ├─Check        │ ✓ Master 1  │
    │ Master 3     │ ✓ Slave 1   │
    ├─Check        │ ✓ Master 2  │
    │ Slave 3      │ ✓ Slave 2   │
    │              │ ✓ Master 3  │
    └─────┬────▶   │ ✓ Slave 3   │
          │        │ ✓ MongoDB   │
          ▼        └─────────────┘
    [Statistics]
          │
          ├─── Total Users
          ├─── Total Courses
          ├─── Total Enrollments
          ├─── Total Revenue
          └─── MongoDB Docs
```

---

## Technology Stack

```
┌──────────────────────────────────────────────────────────────┐
│                       TECHNOLOGY STACK                        │
└──────────────────────────────────────────────────────────────┘

╔═══════════════════╦══════════════╦════════════════════════╗
║ Layer             ║ Technology   ║ Version/Notes          ║
╠═══════════════════╬══════════════╬════════════════════════╣
║ Language          ║ Python       ║ 3.10+                  ║
║ RDBMS             ║ PostgreSQL   ║ 12+ (Production: 14+)  ║
║ NoSQL             ║ MongoDB      ║ 4.4+ (Production: 6+)  ║
║ PostgreSQL Driver ║ psycopg2     ║ 2.9.9                  ║
║ MongoDB Driver    ║ pymongo      ║ 4.6.1                  ║
║ Data Generation   ║ Faker        ║ 22.0.0                 ║
║ Environment       ║ python-dotenv║ 1.0.0                  ║
║ Future API        ║ FastAPI      ║ 0.109.0                ║
║ Testing           ║ pytest       ║ 7.4.4                  ║
╚═══════════════════╩══════════════╩════════════════════════╝
```

---

**This visual documentation provides a comprehensive overview of the distributed database architecture. All diagrams use ASCII art for universal compatibility.**
