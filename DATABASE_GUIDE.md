# 🗄️ UrVote.Rocks Database Guide

## 📋 Overview

This comprehensive guide covers all aspects of the UrVote.Rocks database setup, from development to production deployment on DigitalOcean Managed PostgreSQL.

## 🏗️ Database Architecture

### **Core Tables & Relationships**

```
Users (1) ←→ (Many) Songs/Videos/Visuals
Users (1) ←→ (Many) Votes  
Songs/Videos/Visuals (1) ←→ (Many) Votes
Clients (1) ←→ (Many) Contests
Contests (1) ←→ (Many) Songs
Boards (1) ←→ (Many) Songs/Videos/Visuals
```

## 🚀 Production Database (DigitalOcean)

### **Current Production Setup**

* **Provider:** DigitalOcean Managed PostgreSQL
* **Admin User:** `doadmin`
* **Direct Host:** `urvoterocksdb-do-user-18267829-0.e.db.ondigitalocean.com`
* **Port:** `25060`
* **Default Database:** `defaultdb`
* **SSL:** `sslmode=require` (use CA certificate)
* **Maintenance Window:** Tuesday, 8 PM–12 AM (EDT)
* **Backups:** Enabled; supports point-in-time restore (PITR)

### **Connection Test (Direct Endpoint)**

```bash
PGPASSWORD=Securepass1 psql \
  -U doadmin \
  -h urvoterocksdb-do-user-18267829-0.e.db.ondigitalocean.com \
  -p 25060 \
  -d defaultdb \
  "sslmode=require" -c "select version();"
```

### **Environment Variables (Production)**

```bash
# App Configuration
APP_BASE_URL="https://urvote.rocks"
NODE_ENV="production"

# Database — use pool for app traffic
DATABASE_URL="postgresql://app_user:APP_PASS@POOL_HOST:POOL_PORT/app_db?sslmode=require"

# Database — use direct for migrations/backup jobs
DATABASE_URL_DIRECT="postgresql://doadmin:ADMIN_PASS@urvoterocksdb-do-user-18267829-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# SSL Certificate
PGSSLROOTCERT="./certs/do-ca.crt"
```

## 🏠 Local Development Database

### **Quick Setup with Docker**

```bash
# Start PostgreSQL with Docker Compose
docker-compose up -d postgres

# Or manually create database
sudo -u postgres createdb urvote
sudo -u postgres createuser urvote_user
sudo -u postgres psql -c "ALTER USER urvote_user WITH PASSWORD 'Securepass1';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE urvote TO urvote_user;"
```

### **Local Connection**

```bash
psql -h localhost -U urvote_user -d urvote -W
```

## 📊 Complete Database Schema

### **1. Users Table** - Contest Participants & Voters

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    email_verified BOOLEAN DEFAULT false,
    verification_token VARCHAR(255),
    
    -- Artist Profile Fields
    artist_name VARCHAR(255),
    bio TEXT,
    website VARCHAR(500),
    social_links JSONB,
    profile_image VARCHAR(500),
    is_contestant BOOLEAN DEFAULT false,
    is_voter BOOLEAN DEFAULT true,
    membership_expires_at TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    genre VARCHAR(100),
    years_active VARCHAR(50)
);
```

### **2. Clients Table** - Multi-Client Support

```sql
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    tagline VARCHAR(500),
    description TEXT,
    about TEXT,
    company_info TEXT,
    mission TEXT,
    logo_url VARCHAR(500),
    theme JSONB,
    website_url VARCHAR(500),
    contact_email VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **3. Contests Table** - Contest Management

```sql
CREATE TABLE contests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    max_entries_per_user INTEGER DEFAULT 1,
    voting_enabled BOOLEAN DEFAULT true,
    client_id INTEGER REFERENCES clients(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **4. Boards Table** - Content Organization

```sql
CREATE TABLE boards (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    theme VARCHAR(100),
    user_id BIGINT REFERENCES users(id),
    
    -- Business Information
    website_url VARCHAR(500),
    contact_email VARCHAR(255),
    industry VARCHAR(100),
    business_tagline VARCHAR(255),
    
    -- Social Media
    social_facebook VARCHAR(500),
    social_linkedin VARCHAR(500),
    social_twitter VARCHAR(500),
    social_instagram VARCHAR(500),
    
    -- Media Preferences
    allow_music BOOLEAN DEFAULT true,
    allow_video BOOLEAN DEFAULT true,
    allow_visuals BOOLEAN DEFAULT true,
    max_music_uploads INTEGER DEFAULT 100,
    max_video_uploads INTEGER DEFAULT 50,
    max_visuals_uploads INTEGER DEFAULT 100,
    require_approval BOOLEAN DEFAULT false,
    allow_anonymous_uploads BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **5. Songs Table** - Music Submissions

```sql
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    ai_tools_used TEXT,
    description TEXT,
    license_type VARCHAR(50) DEFAULT 'stream_only',
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    external_link VARCHAR(500),
    url VARCHAR(500),
    linktree VARCHAR(500),
    social_link VARCHAR(500),
    
    -- Creator Information
    creator_website VARCHAR(500),
    creator_linktree VARCHAR(500),
    creator_instagram VARCHAR(500),
    creator_twitter VARCHAR(500),
    creator_youtube VARCHAR(500),
    creator_tiktok VARCHAR(500),
    
    -- Status
    is_approved BOOLEAN DEFAULT false,
    is_rejected BOOLEAN DEFAULT false,
    rejection_reason TEXT,
    
    -- Relationships
    artist_id INTEGER REFERENCES users(id),
    contest_id INTEGER REFERENCES contests(id),
    board_id BIGINT REFERENCES boards(id) ON DELETE CASCADE,
    audio_url VARCHAR(500),
    content_source VARCHAR(50) DEFAULT 'upload',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE
);
```

### **6. Videos Table** - Video Submissions

```sql
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    description TEXT,
    video_type VARCHAR(100),
    file_path VARCHAR(500),
    external_link VARCHAR(500),
    file_size BIGINT,
    file_hash VARCHAR(64),
    
    -- Creator Information (same as songs)
    creator_website VARCHAR(500),
    creator_linktree VARCHAR(500),
    creator_instagram VARCHAR(500),
    creator_twitter VARCHAR(500),
    creator_youtube VARCHAR(500),
    creator_tiktok VARCHAR(500),
    
    -- Status
    is_approved BOOLEAN DEFAULT true,
    is_rejected BOOLEAN DEFAULT false,
    rejection_reason TEXT,
    
    -- Relationships
    artist_id INTEGER REFERENCES users(id),
    board_id BIGINT REFERENCES boards(id) ON DELETE CASCADE,
    content_source VARCHAR(50) DEFAULT 'upload',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE
);
```

### **7. Visuals Table** - Visual Content

```sql
CREATE TABLE visuals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    description TEXT,
    visual_type VARCHAR(100),
    file_path VARCHAR(500),
    external_link VARCHAR(500),
    file_size BIGINT,
    file_hash VARCHAR(64),
    
    -- Creator Information (same as songs)
    creator_website VARCHAR(500),
    creator_linktree VARCHAR(500),
    creator_instagram VARCHAR(500),
    creator_twitter VARCHAR(500),
    creator_youtube VARCHAR(500),
    creator_tiktok VARCHAR(500),
    
    -- Status
    is_approved BOOLEAN DEFAULT true,
    is_rejected BOOLEAN DEFAULT false,
    rejection_reason TEXT,
    
    -- Relationships
    artist_id INTEGER REFERENCES users(id),
    board_id BIGINT REFERENCES boards(id) ON DELETE CASCADE,
    content_source VARCHAR(50) DEFAULT 'upload',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE
);
```

### **8. Votes Table** - Universal Voting System

```sql
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    song_id INTEGER REFERENCES songs(id),
    voter_id INTEGER REFERENCES users(id),
    voter_type VARCHAR(20) DEFAULT 'authenticated',
    
    -- Generic voting fields
    media_type VARCHAR(20), -- 'music', 'video', 'visuals'
    media_id BIGINT,
    vote_type VARCHAR(20) DEFAULT 'like', -- 'like' or 'dislike'
    
    -- Fraud Prevention
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    device_fingerprint VARCHAR(255),
    recaptcha_score VARCHAR(10),
    
    -- GeoIP Data
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 Database Setup & Migration

### **1. Install Dependencies**

```bash
# Install Alembic for migrations
pip install alembic

# Install PostgreSQL client tools
sudo apt install postgresql-client
```

### **2. Run Migrations**

```bash
# Initialize migrations (if not already done)
alembic init alembic

# Create new migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### **3. Create Admin User**

```python
# Run this Python script to create admin user
from app.database import get_db
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    with next(get_db()) as db:
        admin = User(
            email="admin@urvote.rocks",
            username="admin",
            hashed_password=pwd_context.hash("admin_password"),
            is_admin=True,
            is_active=True,
            email_verified=True
        )
        db.add(admin)
        db.commit()
        print("Admin user created successfully!")
```

## 🚀 Production Setup (DigitalOcean)

### **1. Create App Database & User**

```sql
-- Connect as doadmin to defaultdb, then:
CREATE ROLE app_user LOGIN PASSWORD 'REPLACE_WITH_STRONG_SECRET';
CREATE DATABASE app_db OWNER app_user;

-- Optional hardening
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO app_user;

-- Useful extensions
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### **2. Set Up Connection Pool (pgbouncer)**

* UI: Database → Connection Pools → Add Pool
  * Mode: `transaction`
  * DB: `app_db`
  * User: `app_user`
  * Size: ~20
* Save the **pool host/port** for the app's `DATABASE_URL`

### **3. Restrict Access (Trusted Sources)**

* Add app servers and office/static IPs under **Settings → Trusted Sources**

### **4. Download CA Certificate**

* From cluster Overview, **Download CA certificate**
* Store as `certs/do-ca.crt`

## 🔒 Security & Performance

### **1. Database Indexes**

```sql
-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_songs_approved ON songs(is_approved) WHERE is_approved = true;
CREATE INDEX idx_songs_board ON songs(board_id);
CREATE INDEX idx_votes_media ON votes(media_type, media_id);
CREATE INDEX idx_votes_voter ON votes(voter_id, created_at);
CREATE INDEX idx_votes_ip ON votes(ip_address, created_at);

-- Composite indexes for common queries
CREATE INDEX idx_songs_contest_status ON songs(contest_id, is_approved, created_at);
CREATE INDEX idx_votes_geo_time ON votes(country_code, created_at);
```

### **2. Row Level Security (RLS)**

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY user_access_policy ON users
    FOR ALL USING (id = auth.uid() OR auth.role() = 'admin');

CREATE POLICY vote_access_policy ON votes
    FOR ALL USING (voter_id = auth.uid() OR auth.role() = 'admin');
```

### **3. Connection Pooling (Production)**

```python
# In app/database.py
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,           # Maximum connections
    max_overflow=30,        # Additional connections when pool is full
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections every hour
)
```

## 📊 Monitoring & Maintenance

### **1. Backup Strategy**

```bash
# Automated daily backups
#!/bin/bash
BACKUP_DIR="/opt/backups/urvote"
DATE=$(date +%Y%m%d_%H%M%S)

# Local backup
pg_dump -h localhost -U urvote_user urvote > $BACKUP_DIR/urvote_$DATE.sql

# Production backup (using direct endpoint)
PGPASSWORD=$ADMIN_PASSWORD pg_dump \
  -U doadmin \
  -h urvoterocksdb-do-user-18267829-0.e.db.ondigitalocean.com \
  -p 25060 \
  -d app_db \
  "sslmode=require" > $BACKUP_DIR/production_$DATE.sql

# Keep last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

### **2. Performance Monitoring**

```sql
-- Monitor table sizes
SELECT 
    schemaname, 
    tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size 
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Monitor slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### **3. Regular Maintenance**

```sql
-- Clean up and update statistics
VACUUM ANALYZE;

-- Rebuild indexes
REINDEX DATABASE urvote;

-- Check for unused indexes
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

## 🔄 Data Migration

### **From Custom Format Dump**

```bash
# Create dump from source
pg_dump -Fc -h OLD_HOST -U OLD_USER -d OLD_DB -f backup.dump

# Restore into new cluster
PGPASSWORD=YOUR_ADMIN_PASSWORD pg_restore \
  -U doadmin \
  -h urvoterocksdb-do-user-18267829-0.e.db.ondigitalocean.com \
  -p 25060 \
  -d app_db \
  --no-owner --no-privileges --verbose backup.dump
```

### **From Plain SQL File**

```bash
PGPASSWORD=YOUR_ADMIN_PASSWORD psql \
  -U doadmin \
  -h urvoterocksdb-do-user-18267829-0.e.db.ondigitalocean.com \
  -p 25060 \
  -d app_db \
  "sslmode=require" -f ./backup.sql
```

### **Post-Restore Ownership**

```sql
REASSIGN OWNED BY doadmin TO app_user;
ALTER DATABASE app_db OWNER TO app_user;
```

## 📈 Scaling Strategy

### **Phase 1: Single Database (Current)**
- All tables in one PostgreSQL instance
- Suitable for up to 10,000 users and 1,000 songs
- Good for MVP and initial launch

### **Phase 2: Read Replicas**
- Add read replicas for leaderboards and public queries
- Primary: Write operations (uploads, votes, admin)
- Replica: Read operations (leaderboards, song listings)

### **Phase 3: Microservices Split**
- User Service DB: users, authentication
- Contest Service DB: songs, contests, votes
- File Service DB: file metadata, storage

## 🎯 Next Steps

1. **✅ Database setup complete** - Both local and production configured
2. **✅ Schema defined** - All tables and relationships established
3. **✅ Migrations ready** - Alembic configured for schema changes
4. **🔄 Security hardening** - Implement RLS and additional indexes
5. **📊 Monitoring setup** - Add performance monitoring and alerts
6. **🔄 Backup automation** - Set up automated backup procedures

## 🆘 Troubleshooting

### **Connection Issues**

```bash
# Test local connection
psql -h localhost -U urvote_user -d urvote -c "SELECT version();"

# Test production connection
PGPASSWORD=YOUR_PASSWORD psql \
  -U doadmin \
  -h urvoterocksdb-do-user-18267829-0.e.db.ondigitalocean.com \
  -p 25060 \
  -d defaultdb \
  "sslmode=require" -c "SELECT version();"
```

### **Migration Issues**

```bash
# Check migration status
alembic current

# Check migration history
alembic history

# Rollback if needed
alembic downgrade -1

# Force to specific revision
alembic stamp <revision_id>
```

### **Performance Issues**

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 5;

-- Check table bloat
SELECT schemaname, tablename, n_dead_tup, n_live_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 0;
```

---

**Last Updated:** December 2024  
**Database Version:** PostgreSQL 15+  
**Migration Tool:** Alembic  
**Production:** DigitalOcean Managed PostgreSQL
===========================================================================
Perfect! That's a great architecture decision! 🎯 Let me break down your data strategy at a high level:

## 🏗️ **Your Data Architecture Strategy**

### **☁️ DigitalOcean Spaces (File Storage)**
**What goes here:**
- �� **Music files** (.mp3, .wav, .flac, .m4a)
- �� **Video files** (.mp4, .mov, .avi)
- ��️ **Images** (.jpg, .png, .gif, .webp)
- 📄 **Documents** (.pdf, .docx) if needed

**Benefits:**
- ✅ Unlimited storage
- ✅ CDN delivery
- ✅ Cost-effective
- ✅ Easy to manage

### **🗄️ DigitalOcean Managed PostgreSQL (Database)**
**What goes here:**
- 👥 **User accounts** (voters, board owners, content uploaders)
- ��️ **Voting data** (who voted for what, when)
- 🏢 **Board information** (board owners, settings, themes)
- �� **Content metadata** (titles, descriptions, file paths in Spaces)
- �� **Contest data** (contests, rules, winners)
- 🔗 **Relationships** (who owns what, what belongs where)

## 📋 **Data Flow Example**

```
User uploads music file:
1. File → DigitalOcean Spaces (actual .mp3 file)
2. Metadata → PostgreSQL (title, artist, file path in Spaces)
3. User info → PostgreSQL (who uploaded it)
4. Board info → PostgreSQL (which board it belongs to)
```

## 🎯 **Why This Architecture Works**

### **Spaces for Files:**
- **Fast delivery** via CDN
- **Scalable storage** (unlimited)
- **Cost-effective** (pay per GB)
- **Easy backup** (automatic)

### **PostgreSQL for Data:**
- **Fast queries** for user data
- **ACID compliance** for transactions
- **Complex relationships** (user → board → content → votes)
- **Real-time updates** (voting, leaderboards)

## 🔄 **Data Relationships**

```
Users (voters, board owners, uploaders)
    ↓
Boards (content organization)
    ↓
Content Metadata (songs, videos, images)
    ↓
File References (pointing to Spaces URLs)
    ↓
Votes (user interactions)
```

## 💡 **Key Benefits of This Approach**

1. **Separation of Concerns**: Files vs. Data
2. **Performance**: Fast file delivery + fast database queries
3. **Scalability**: Each service scales independently
4. **Cost**: Pay for what you use
5. **Reliability**: Managed services handle the heavy lifting

## 🚀 **Implementation Strategy**

1. **Keep current local setup** for development
2. **Set up DigitalOcean Spaces** for file storage
3. **Set up managed PostgreSQL** for production data
4. **Update your app** to use Spaces for files
5. **Migrate data** when ready for production

               List of relations
 Schema |      Name       | Type  |    Owner    
--------+-----------------+-------+-------------
 public | alembic_version | table | urvote_user
 public | boards          | table | urvote_user
 public | clients         | table | urvote_user
 public | contests        | table | urvote_user
 public | songs           | table | urvote_user
 public | users           | table | urvote_user
 public | videos          | table | urvote_user
 public | visuals         | table | urvote_user
 public | votes           | table | urvote_user
(9 rows)