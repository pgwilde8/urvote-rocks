Great question! The anonymous voting data is saved in the **Vote table** in your database. Let me show you exactly where and how it's stored:

## Database Storage

### **Vote Table Structure**
```sql
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    -- Anonymous voting fields
    voter_email VARCHAR(255),           -- Email address (indexed)
    voter_name VARCHAR(255),            -- Optional name
    voter_type VARCHAR(20) DEFAULT 'anonymous',
    
    -- Content being voted on
    media_type VARCHAR(20),             -- "music", "video", "visuals"
    media_id BIGINT,                    -- ID of the content
    
    -- Fraud prevention
    ip_address VARCHAR(45),             -- IPv6 compatible
    user_agent TEXT,                    -- Browser info
    device_fingerprint VARCHAR(255),    -- Unique device ID
    recaptcha_score VARCHAR(10),        -- reCAPTCHA score
    
    -- Rate limiting
    votes_per_email_per_day INTEGER DEFAULT 1,
    
    -- GeoIP data
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## What Gets Saved

When someone votes anonymously, this data is stored:

```python
# Example vote record
{
    "id": 123,
    "voter_email": "john@example.com",
    "voter_name": "John Doe",
    "voter_type": "anonymous",
    "media_type": "music",
    "media_id": 456,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "device_fingerprint": "a1b2c3d4e5f6...",
    "recaptcha_score": "0.9",
    "votes_per_email_per_day": 1,
    "country_code": "US",
    "region": "California",
    "city": "San Francisco",
    "created_at": "2024-01-15 10:30:00"
}
```

## Marketing Benefits

This gives you **powerful marketing data**:

1. **Email addresses** - for follow-up campaigns
2. **Voting patterns** - who votes on what
3. **Geographic data** - where your users are
4. **Engagement metrics** - how often people vote
5. **Content preferences** - what gets the most votes

## Privacy & Security

- **No passwords stored** - just email + name
- **Device fingerprinting** - prevents duplicate votes
- **Rate limiting** - 1 vote per email per day
- **reCAPTCHA protection** - blocks bots
- **IP tracking** - monitors suspicious activity

## Query Examples

You can easily query this data for analytics:

```sql
-- Get all votes for a specific board
SELECT voter_email, voter_name, created_at 
FROM votes 
WHERE media_id IN (
    SELECT id FROM songs WHERE board_id = 1
);

-- Get voting statistics
SELECT 
    COUNT(*) as total_votes,
    COUNT(DISTINCT voter_email) as unique_voters,
    country_code
FROM votes 
GROUP BY country_code;
```

The anonymous voting system gives you **maximum user acquisition** while still collecting valuable marketing data for your angel investor pitch! 🚀