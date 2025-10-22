<div align="center">

# 🎓 Distributed Database Management System
### *For Global E-Learning Platforms*

**Scalable • Distributed • High-Performance**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-5.0+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

*A production-ready distributed database system built to handle millions of users, courses, and transactions across multiple geographic regions with master-slave replication, horizontal sharding, and NoSQL integration.*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📑 Table of Contents

- [About the Project](#-about-the-project)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Folder Structure](#-folder-structure)
- [Features](#-features)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
  - [Environment Configuration](#environment-configuration)
- [Running the Project](#-running-the-project)
- [Usage Examples](#-usage-examples)
- [Troubleshooting](#-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)
- [Credits](#-credits)

---

## 🌍 About the Project

### The Problem

Modern e-learning platforms serve millions of users worldwide, requiring:
- ⚡ **Low-latency access** across different geographic regions
- 💪 **High availability** with automatic failover
- 📈 **Horizontal scalability** to handle growing user bases
- 🔄 **Data consistency** across distributed nodes
- 🎯 **Efficient query performance** for complex operations

### The Solution

This project implements a **production-grade Distributed Database Management System (DDBMS)** that addresses these challenges through:

- 🌐 **Geographic Sharding**: Data partitioned by region (North America, Europe, Asia)
- 🔁 **Master-Slave Replication**: Write to masters, read from slaves for optimal performance
- 🗄️ **Hybrid Database Architecture**: PostgreSQL for structured data + MongoDB for unstructured content
- 🔌 **Connection Pooling**: Efficient resource management with automatic connection recycling
- 🎯 **Smart Query Routing**: Automatic routing to appropriate shard and node based on operation type

### Built For

- 👨‍🎓 Students learning distributed systems
- 👨‍💻 Developers building scalable applications
- 🏢 Companies requiring multi-region database solutions
- 📚 Educational platforms with global user bases

---

## 🏗️ System Architecture

```
                    🌍 Global E-Learning Platform
                              │
                    ┌─────────┴─────────┐
                    │   FastAPI Layer   │
                    │  (REST API + JWT) │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐   ┌────▼─────┐   ┌────▼─────┐
        │  Shard 1  │   │ Shard 2  │   │ Shard 3  │
        │ Americas  │   │  Europe  │   │   Asia   │
        └─────┬─────┘   └────┬─────┘   └────┬─────┘
              │              │              │
        ┌─────┴─────┐   ┌────┴─────┐   ┌────┴─────┐
        │  Master   │   │ Master   │   │ Master   │
        │  :5432    │   │ :5433    │   │ :5434    │
        └─────┬─────┘   └────┬─────┘   └────┬─────┘
              │              │              │
        ┌─────┴─────┐   ┌────┴─────┐   ┌────┴─────┐
        │  Slave    │   │  Slave   │   │  Slave   │
        │  :5435    │   │  :5436   │   │  :5437   │
        └───────────┘   └──────────┘   └──────────┘

                    ┌───────────────────┐
                    │   MongoDB Atlas   │
                    │ Course Content &  │
                    │ User Preferences  │
                    └───────────────────┘
```

### Key Design Principles

- **Master-Slave Replication**: Write operations → Master nodes, Read operations → Slave nodes
- **Horizontal Sharding**: Data partitioned by geographic region for locality
- **3NF Normalized Schema**: Optimized PostgreSQL schema with 13 tables
- **Stored Procedures**: Complex business logic at database level
- **Automatic Triggers**: Real-time progress tracking and rating calculations

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | Core application logic |
| **RDBMS** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white) | Structured data storage |
| **NoSQL** | ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white) | Unstructured content |
| **API Framework** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) | RESTful API endpoints |
| **Auth** | ![JWT](https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens&logoColor=white) | Token-based authentication |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=white) | Unit & integration tests |
| **Cloud DB** | ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?logo=supabase&logoColor=white) | Managed PostgreSQL (optional) |
| **Cloud DB** | ![MongoDB Atlas](https://img.shields.io/badge/Atlas-47A248?logo=mongodb&logoColor=white) | Managed MongoDB (optional) |

</div>

### Dependencies

```python
psycopg2-binary==2.9.9      # PostgreSQL adapter
pymongo==4.6.1              # MongoDB driver
fastapi==0.109.0            # Web framework
pyjwt==2.8.0                # JWT authentication
faker==22.0.0               # Sample data generation
python-dotenv==1.0.0        # Environment management
```

---

## 📁 Folder Structure

```
DistributedDatabaseManagementSystem/
│
├── 📂 api/                          # REST API Layer
│   ├── main.py                      # FastAPI application entry point
│   ├── routers/                     # API route handlers
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── users.py                 # User management
│   │   ├── courses.py               # Course operations
│   │   ├── enrollments.py           # Enrollment tracking
│   │   └── payments.py              # Payment processing
│   ├── schemas/                     # Pydantic models
│   ├── services/                    # Business logic layer
│   └── utils/                       # Auth & rate limiting
│
├── 📂 db/                           # Database Layer
│   ├── config/                      # Database configuration
│   │   └── database_config.py       # Connection settings
│   ├── postgres_scripts/            # PostgreSQL implementation
│   │   ├── schema.sql               # 3NF normalized schema
│   │   ├── stored_procedures.sql    # Business logic procedures
│   │   ├── connection_manager.py    # Connection pooling
│   │   ├── user_crud.py             # User operations
│   │   ├── course_crud.py           # Course operations
│   │   ├── enrollment_crud.py       # Enrollment operations
│   │   └── payment_crud.py          # Payment operations
│   ├── mongo_scripts/               # MongoDB implementation
│   │   └── connection_manager.py    # Content & preferences
│   ├── setup_database.py            # Database initialization
│   ├── sample_data_generator.py     # Test data generator
│   ├── health_check.py              # Health monitoring
│   └── DATABASE_GUIDE.md            # Complete documentation
│
├── 📂 networking/                   # Inter-node communication
│   ├── tcp_server.py                # TCP server implementation
│   ├── tcp_client.py                # TCP client
│   ├── udp_server.py                # UDP server
│   └── connection_pool.py           # Network connection pooling
│
├── 📂 tests/                        # Test suite
│   ├── test_api_endpoints.py        # API tests
│   ├── test_business_logic.py       # Service layer tests
│   ├── test_db_crud.py              # Database tests
│   └── test_integration.py          # End-to-end tests
│
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 requirements.txt              # Python dependencies
├── 📄 LICENSE                       # MIT License
└── 📄 README.md                     # This file

```

---

## ✨ Features

### Database Layer
- ✅ **Master-Slave Replication** - High availability with automatic failover
- ✅ **Geographic Sharding** - Data partitioned by region (NA, EU, Asia)
- ✅ **Connection Pooling** - Efficient resource management
- ✅ **3NF Normalized Schema** - 13 tables with optimal relationships
- ✅ **40+ Indexes** - Optimized query performance
- ✅ **20+ Stored Procedures** - Complex operations at DB level
- ✅ **5 Automatic Triggers** - Real-time data updates
- ✅ **MongoDB Integration** - Video content & user preferences

### API Layer
- ✅ **RESTful Endpoints** - Complete CRUD operations
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Rate Limiting** - DDoS protection
- ✅ **CORS Support** - Cross-origin requests
- ✅ **API Versioning** - /api/v1 namespace
- ✅ **Error Handling** - Comprehensive exception management

### Business Features
- ✅ **User Management** - Students, instructors, admins
- ✅ **Course Management** - Curriculum, modules, lessons
- ✅ **Enrollment Tracking** - Progress monitoring
- ✅ **Payment Processing** - Transactions & invoices
- ✅ **Review System** - Course ratings & feedback
- ✅ **Analytics** - Revenue, enrollment statistics

### DevOps
- ✅ **Health Monitoring** - Database status checks
- ✅ **Sample Data Generator** - Realistic test data
- ✅ **Comprehensive Tests** - Unit & integration coverage
- ✅ **Environment Config** - .env file support
- ✅ **Documentation** - 900+ lines of guides

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- 🐍 **Python 3.10+** - [Download here](https://www.python.org/downloads/)
- 📦 **pip** - Python package installer (included with Python)
- 🔧 **Git** - [Download here](https://git-scm.com/downloads)
- 💻 **VS Code** (Recommended) - [Download here](https://code.visualstudio.com/)

You'll also need accounts for:
- 🐘 **PostgreSQL** - [Supabase](https://supabase.com/) (Free tier) OR local PostgreSQL
- 🍃 **MongoDB** - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (Free tier) OR local MongoDB

---

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/distributed-elearning-dbms.git
cd distributed-elearning-dbms
```

#### 2️⃣ Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

<details>
<summary>💡 <b>Optional: Use Virtual Environment</b> (Click to expand)</summary>

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
</details>

---

### Database Setup

#### Option A: Using Supabase (PostgreSQL) 🌐

**Step 1: Create Supabase Project**

1. Go to [Supabase](https://supabase.com/) and sign up
2. Click **"New Project"**
3. Fill in:
   - **Name**: `elearning-db`
   - **Database Password**: (save this!)
   - **Region**: Choose closest to you
4. Wait for project to be ready (~2 minutes)

**Step 2: Get Connection String**

1. Go to **Project Settings** → **Database**
2. Copy the **Connection String** (URI format)
3. It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`

**Step 3: Create Multiple Databases (for sharding simulation)**

```sql
-- Run in Supabase SQL Editor
CREATE DATABASE elearning_na;
CREATE DATABASE elearning_eu;
CREATE DATABASE elearning_asia;
```

#### Option B: Local PostgreSQL 🖥️

```bash
# Install PostgreSQL (if not installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Start PostgreSQL service
# Windows: Already running after install
# Mac: brew services start postgresql
# Linux: sudo service postgresql start

# Create databases
psql -U postgres
CREATE DATABASE elearning_na;
CREATE DATABASE elearning_eu;
CREATE DATABASE elearning_asia;
\q
```

---

#### MongoDB Setup (Atlas) 🍃

**Step 1: Create MongoDB Atlas Cluster**

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Sign up/Sign in
3. Click **"Build a Database"** → Choose **FREE** tier
4. Select a **Cloud Provider** and **Region**
5. Name your cluster: `elearning-cluster`
6. Click **"Create"**

**Step 2: Configure Database Access**

1. Go to **Database Access** → **Add New Database User**
2. Choose **Password** authentication
3. Username: `admin` (or your choice)
4. Password: (auto-generate and save it!)
5. **Database User Privileges**: Read and write to any database
6. Click **"Add User"**

**Step 3: Configure Network Access**

1. Go to **Network Access** → **Add IP Address**
2. Click **"Allow Access from Anywhere"** (for development)
   - IP: `0.0.0.0/0`
3. Click **"Confirm"**

**Step 4: Get Connection String**

1. Go to **Database** → **Connect** → **Connect your application**
2. Driver: **Python**, Version: **3.12 or later**
3. Copy the connection string:
   ```
   mongodb+srv://admin:<password>@elearning-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<password>` with your actual password

---

### Environment Configuration

#### 1️⃣ Create `.env` File

```bash
# Copy the example template
cp .env.example .env
```

#### 2️⃣ Edit `.env` File

Open `.env` in VS Code and fill in your credentials:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# PostgreSQL Configuration (Supabase or Local)
# For Supabase: Use your connection string details
# For Local: Use localhost

# Master Nodes (For simulation, use same host with different ports)
PG_MASTER_NA_HOST=db.xxxsupabase.co    # Or localhost
PG_MASTER_NA_PORT=5432
PG_MASTER_EU_HOST=db.xxxsupabase.co    # Or localhost
PG_MASTER_EU_PORT=5432                  # Same for Supabase
PG_MASTER_ASIA_HOST=db.xxxsupabase.co  # Or localhost
PG_MASTER_ASIA_PORT=5432

# Slave Nodes (For dev, same as master)
PG_SLAVE_NA_HOST=db.xxxsupabase.co
PG_SLAVE_NA_PORT=5432
PG_SLAVE_EU_HOST=db.xxxsupabase.co
PG_SLAVE_EU_PORT=5432
PG_SLAVE_ASIA_HOST=db.xxxsupabase.co
PG_SLAVE_ASIA_PORT=5432

# PostgreSQL Credentials
PG_USER=postgres
PG_PASSWORD=your-supabase-password-here

# MongoDB Atlas Configuration
MONGO_HOST=elearning-cluster.xxxxx.mongodb.net
MONGO_PORT=27017
MONGO_DATABASE=elearning_content
MONGO_USER=admin
MONGO_PASSWORD=your-mongodb-password-here
```

<details>
<summary>📝 <b>Full Connection String Format</b> (for advanced users)</summary>

For MongoDB Atlas, you can also use the full URI:

```bash
# Replace YOUR_USERNAME, YOUR_PASSWORD, YOUR_CLUSTER with your actual values
MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/elearning_content?retryWrites=true&w=majority
```

For Supabase PostgreSQL:

```bash
# Replace YOUR_PASSWORD and YOUR_PROJECT_REF with your actual values
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
```
</details>

---

## 🎯 Running the Project

### 1️⃣ Initialize Databases

```bash
# Navigate to db folder
cd db

# Run setup script (creates schema, procedures, indexes)
python setup_database.py
```

**Expected Output:**
```
🔧 Setting up PostgreSQL Databases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Connected to Shard 1 (North America)
✓ Database 'elearning_na' ready
✓ Schema loaded successfully
✓ Stored procedures created
✓ Indexes created (13 indexes)

✓ PostgreSQL setup completed

🍃 Setting up MongoDB Collections
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Connected to MongoDB Atlas
✓ Collection 'course_content' created
✓ Collection 'user_preferences' created
✓ Indexes created

✅ All databases initialized successfully!
```

### 2️⃣ Generate Sample Data

```bash
# Generate realistic test data
python sample_data_generator.py
```

**Expected Output:**
```
📊 Generating Sample Data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Created 100 students
✓ Created 20 instructors
✓ Created 50 courses
✓ Created 200 enrollments
✓ Created 150 transactions
✓ Generated MongoDB content documents

✅ Sample data generated successfully!
```

### 3️⃣ Run Health Check

```bash
# Verify all connections
python health_check.py
```

**Expected Output:**
```
🏥 System Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL Status:
  ✓ Shard 1 Master (NA): HEALTHY
  ✓ Shard 1 Slave (NA):  HEALTHY
  ✓ Shard 2 Master (EU): HEALTHY
  ✓ Shard 2 Slave (EU):  HEALTHY
  ✓ Shard 3 Master (AS): HEALTHY
  ✓ Shard 3 Slave (AS):  HEALTHY

MongoDB Status:
  ✓ Atlas Cluster: HEALTHY
  ✓ Ping: 12ms

Data Statistics:
  👥 Users: 120
  📚 Courses: 50
  🎓 Enrollments: 200
  💰 Revenue: $12,450.00

✅ All systems operational!
```

### 4️⃣ Run the API Server

```bash
# Navigate to api folder
cd ../api

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

🎉 **Your API is now live!** Visit:
- 📖 Interactive Docs: http://localhost:8000/docs
- 🔧 API Health: http://localhost:8000/api/v1/health

---

## 💡 Usage Examples

### Example 1: Create a New User

```python
from db.postgres_scripts.user_crud import UserCRUD

user_crud = UserCRUD()

# Create student account
user_id = user_crud.create_user(
    email="jane.doe@example.com",
    password="SecurePass123!",
    first_name="Jane",
    last_name="Doe",
    user_type="student",
    region="north_america",
    country="United States",
    city="New York"
)

print(f"✅ User created with ID: {user_id}")
```

**Output:**
```
✅ User created with ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Example 2: Create and Publish a Course

```python
from db.postgres_scripts.course_crud import CourseCRUD

course_crud = CourseCRUD()

# Create course
course_id = course_crud.create_course(
    course_code="PY101",
    title="Python for Beginners",
    description="Learn Python from scratch",
    instructor_id=instructor_id,
    region="north_america",
    category_id=1,
    level="beginner",
    price=49.99,
    duration_weeks=8,
    max_enrollments=100
)

# Publish course
course_crud.publish_course(course_id, "north_america")

print(f"✅ Course published: {course_id}")
```

### Example 3: Enroll User and Track Progress

```python
from db.postgres_scripts.enrollment_crud import EnrollmentCRUD

enrollment_crud = EnrollmentCRUD()

# Enroll student
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
    time_spent=25  # minutes
)

print(f"✅ Progress updated for enrollment: {enrollment_id}")
```

### Example 4: API Request (Using cURL)

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!",
    "full_name": "John Student",
    "role": "student"
  }'
```

**Response:**
```json
{
  "user_id": "abc123",
  "email": "student@example.com",
  "message": "User registered successfully"
}
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

<details>
<summary><b>❌ PostgreSQL Connection Refused</b></summary>

**Error:**
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solutions:**
1. Check if PostgreSQL is running:
   ```bash
   # Windows
   services.msc  # Look for PostgreSQL service
   
   # Mac/Linux
   sudo service postgresql status
   ```

2. Verify `.env` credentials match your database
3. For Supabase: Check if your IP is whitelisted
4. Test connection:
   ```bash
   psql -h your-host -U postgres -d elearning_na
   ```
</details>

<details>
<summary><b>❌ MongoDB Authentication Failed</b></summary>

**Error:**
```
pymongo.errors.OperationFailure: Authentication failed
```

**Solutions:**
1. Verify username/password in `.env`
2. Check MongoDB Atlas → Database Access → User exists
3. Ensure Network Access allows your IP (`0.0.0.0/0` for dev)
4. Test connection string in MongoDB Compass
</details>

<details>
<summary><b>❌ Module Not Found Error</b></summary>

**Error:**
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install psycopg2-binary
```
</details>

<details>
<summary><b>❌ Port Already in Use</b></summary>

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Windows - Find process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```
</details>

<details>
<summary><b>❌ Schema Already Exists Error</b></summary>

**Solution:**
Drop existing tables and rerun setup:

```sql
-- In PostgreSQL
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

Then rerun:
```bash
python setup_database.py
```
</details>

---

## 🔮 Future Enhancements

### Planned Features

- [ ] 🐳 **Docker Containerization** - Complete Docker Compose setup
- [ ] ☸️ **Kubernetes Orchestration** - Auto-scaling and load balancing
- [ ] 📊 **Real-time Analytics Dashboard** - Data visualization with Grafana
- [ ] 🔐 **OAuth 2.0 Integration** - Google/GitHub social login
- [ ] 💬 **WebSocket Support** - Real-time notifications
- [ ] 🤖 **AI-Powered Recommendations** - Personalized course suggestions
- [ ] 📧 **Email Service Integration** - SendGrid/AWS SES
- [ ] 💳 **Payment Gateway Integration** - Stripe/PayPal
- [ ] 🌐 **CDN Integration** - CloudFront for video delivery
- [ ] 📱 **Mobile App Backend** - GraphQL API layer
- [ ] 🔍 **Elasticsearch Integration** - Full-text search
- [ ] 📈 **Prometheus Monitoring** - System metrics and alerting

### Architecture Improvements

- [ ] Implement Raft consensus for true distributed coordination
- [ ] Add Redis caching layer for frequently accessed data
- [ ] Implement event sourcing with Kafka
- [ ] Add backup and disaster recovery automation
- [ ] Implement multi-region failover

---

## 🤝 Contributing

We love contributions! ❤️ Here's how you can help:

### How to Contribute

1. **Fork the Repository**
   ```bash
   # Click the Fork button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/distributed-elearning-dbms.git
   cd distributed-elearning-dbms
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "✨ Add amazing feature"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Describe your changes in detail

### Contribution Guidelines

- ✅ Write clear commit messages
- ✅ Include tests for new features
- ✅ Update documentation as needed
- ✅ Follow Python PEP 8 style guide
- ✅ Add docstrings to functions
- ❌ Don't commit `.env` files
- ❌ Don't include credentials in code

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what's best for the community

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Maulishka Srivastava

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

See [LICENSE](LICENSE) for full text.

---

## 💖 Credits

<div align="center">

### Developed with 💜 by **Maulishka Srivastava** 🌸

*"Building scalable systems, one shard at a time"*

---

### Special Thanks

- 🙏 **Open Source Community** - For amazing tools and libraries
- 📚 **Supabase** - For excellent PostgreSQL hosting
- 🍃 **MongoDB Atlas** - For reliable NoSQL database
- ⚡ **FastAPI Team** - For the incredible web framework
- 🐍 **Python Community** - For continuous support

---

### 🌟 If you found this project helpful, please give it a star!

[![GitHub stars](https://img.shields.io/github/stars/yourusername/distributed-elearning-dbms?style=social)](https://github.com/yourusername/distributed-elearning-dbms/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/distributed-elearning-dbms?style=social)](https://github.com/yourusername/distributed-elearning-dbms/network/members)

---

**Built for learners, by learners** 🚀

[⬆ Back to Top](#-distributed-database-management-system)

</div>
