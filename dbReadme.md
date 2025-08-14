## 🗄️ **Database Architecture Overview**

### **Core Tables & Relationships**

```
Users (1) ←→ (Many) Songs
Users (1) ←→ (Many) Votes  
Songs (1) ←→ (Many) Votes
Contests (1) ←→ (Many) Songs (optional)
```

## 📊 **Detailed Database Schema**

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
    profile_data JSONB, -- For future profile features
    last_login TIMESTAMP WITH TIME ZONE
);
```

**Purpose**: 
- Contest participants who submit songs
- Voters who participate in contests
- Admin users who moderate content
- Email verification and account management

### **2. Songs Table** - Contest Submissions
```sql
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    ai_tools_used TEXT NOT NULL,
    description TEXT,
    license_type VARCHAR(50) DEFAULT 'stream_only',
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    external_link VARCHAR(500), -- YouTube/SoundCloud links
    is_approved BOOLEAN DEFAULT false,
    is_rejected BOOLEAN DEFAULT false,
    rejection_reason TEXT,
    artist_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB -- For flexible additional data
);
```

**Purpose**:
- Store all song submissions
- Track approval/rejection status
- Link to uploaded files or external sources
- Store AI tool information and licensing

### **3. Votes Table** - Voting & Fraud Prevention
```sql
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    song_id INTEGER REFERENCES songs(id) NOT NULL,
    voter_id INTEGER REFERENCES users(id) NOT NULL,
    ip_address VARCHAR(45) NOT NULL, -- IPv6 compatible
    user_agent TEXT,
    device_fingerprint VARCHAR(255),
    recaptcha_score VARCHAR(10),
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    vote_weight DECIMAL(3,2) DEFAULT 1.00, -- For future weighted voting
    is_suspicious BOOLEAN DEFAULT false,
    fraud_flags JSONB -- Store multiple fraud indicators
);
```

**Purpose**:
- Track all voting activity
- Implement fraud prevention
- GeoIP tracking for contest eligibility
- Daily voting limits enforcement

### **4. Contests Table** - Contest Management
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
    rules TEXT,
    prizes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB -- Flexible contest configuration
);
```

**Purpose**:
- Manage multiple contests
- Set contest timeframes and rules
- Configure voting parameters
- Track contest-specific settings

## 🔧 **Database Setup Process**

### **Step 1: Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server postgresql-contrib
sudo postgresql-setup initdb
```

### **Step 2: Create Database & User**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE urvote;
CREATE USER urvote_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE urvote TO urvote_user;
ALTER USER urvote_user CREATEDB;
\q
```

### **Step 3: Configure PostgreSQL**
```bash
# Edit postgresql.conf for performance
sudo nano /etc/postgresql/14/main/postgresql.conf

# Key settings for production:
shared_buffers = 256MB          # 25% of RAM
effective_cache_size = 1GB      # 75% of RAM
work_mem = 4MB                  # Per connection
maintenance_work_mem = 64MB     # For maintenance operations
```

### **Step 4: Run Database Migrations**
```bash
# Install Alembic
pip install alembic

# Initialize migrations (already done)
# alembic init alembic

# Run initial migration
alembic upgrade head
```

## 🚀 **Production Database Considerations**

### **1. Connection Pooling**
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

### **2. Database Indexes**
```sql
-- Performance indexes
CREATE INDEX idx_songs_approved ON songs(is_approved) WHERE is_approved = true;
CREATE INDEX idx_votes_song_date ON votes(song_id, created_at);
CREATE INDEX idx_votes_voter_date ON votes(voter_id, created_at);
CREATE INDEX idx_users_email_verified ON users(email_verified) WHERE email_verified = true;

-- Composite indexes for common queries
CREATE INDEX idx_songs_contest_status ON songs(contest_id, is_approved, created_at);
CREATE INDEX idx_votes_geo_time ON votes(country_code, created_at);
```

### **3. Partitioning for Large Scale**
```sql
-- Partition votes table by date for high-volume voting
CREATE TABLE votes_2024_01 PARTITION OF votes
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE votes_2024_02 PARTITION OF votes
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## �� **Database Scaling Strategy**

### **Phase 1: Single Database (Current)**
- All tables in one PostgreSQL instance
- Suitable for up to 10,000 users and 1,000 songs
- Good for MVP and initial launch

### **Phase 2: Read Replicas**
```bash
# Add read replicas for leaderboards and public queries
# Primary: Write operations (uploads, votes, admin)
# Replica: Read operations (leaderboards, song listings)
```

### **Phase 3: Microservices Split**
```
- User Service DB: users, authentication
- Contest Service DB: songs, contests, votes
- File Service DB: file metadata, storage
```

## 🔒 **Security & Backup**

### **1. Database Security**
```sql
-- Restrict user permissions
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM urvote_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO urvote_user;

-- Row Level Security (RLS)
ALTER TABLE songs ENABLE ROW LEVEL SECURITY;
CREATE POLICY song_access_policy ON songs
    FOR ALL USING (is_approved = true OR auth.uid() = artist_id);
```

### **2. Backup Strategy**
```bash
# Automated daily backups
#!/bin/bash
BACKUP_DIR="/opt/backups/urvote"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U urvote_user urvote > $BACKUP_DIR/urvote_$DATE.sql

# Keep last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

### **3. Monitoring & Maintenance**
```sql
-- Regular maintenance tasks
VACUUM ANALYZE;  -- Clean up and update statistics
REINDEX DATABASE urvote;  -- Rebuild indexes

-- Monitor table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size 
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 💾 **Data Storage Requirements**

### **File Storage Strategy**
```
/opt/urvote/uploads/
├── 2024/
│   ├── 01/  # January submissions
│   ├── 02/  # February submissions
│   └── ...
├── temp/     # Temporary uploads
└── processed/ # Processed and validated files
```

### **Database Size Estimates**
- **Users**: ~1KB per user (10,000 users = 10MB)
- **Songs**: ~2KB per song (1,000 songs = 2MB)
- **Votes**: ~500 bytes per vote (100,000 votes = 50MB)
- **Total**: ~100MB for 10K users, 1K songs, 100K votes

## 🎯 **Next Steps for Database Setup**

1. **Install PostgreSQL** on your server
2. **Create database and user** with proper permissions
3. **Configure environment variables** in `.env` file
4. **Run migrations** with `alembic upgrade head`
5. **Create admin user** using the Python script
6. **Test database connections** and basic operations
7. **Set up monitoring** and backup procedures

    client_name    |           contest_name            | is_active 
-------------------+-----------------------------------+-----------
 PayPortPro        | Patriotic AI Music Challenge 2024 | t
 Sound of Chi      | Community Playlist Contest        | t
 Jericho Homestead | The House of Mary & Joseph        | t
 Sound of Chi      | Community Playlist Contest        | t
 Jericho Homestead | The House of Mary & Joseph        | t
 Sound of Chi      | Community Playlist Contest        | t
 Jericho Homestead | The House of Mary & Joseph        | t
(7 rows)