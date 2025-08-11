# UrVote.Rocks Setup Guide

This guide will help you set up the UrVote.Rocks contest platform on your server.

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- Nginx (optional, for production)

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone <your-repo-url>
cd urvote

# Copy environment file
cp env.example .env

# Edit environment variables
nano .env

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Manual Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres createdb urvote
sudo -u postgres createuser urvote_user
sudo -u postgres psql -c "ALTER USER urvote_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE urvote TO urvote_user;"

# Run database migrations
alembic upgrade head
```

### 3. Environment Configuration

Copy and edit the environment file:

```bash
cp env.example .env
nano .env
```

Key settings to configure:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Random secret for JWT tokens
- `UPLOAD_DIR`: Directory for file uploads
- `REDIS_URL`: Redis connection (optional)

### 4. File Permissions

```bash
# Ensure upload directory exists and has proper permissions
sudo mkdir -p /opt/urvote/uploads
sudo chown -R adminrocks:adminrocks /opt/urvote
chmod 755 /opt/urvote/uploads
```

### 5. Start the Application

```bash
# Development mode
python start.py

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

## Production Deployment

### 1. Systemd Service

Create `/etc/systemd/system/urvote.service`:

```ini
[Unit]
Description=UrVote.Rocks Contest Platform
After=network.target postgresql.service

[Service]
Type=exec
User=adminrocks
Group=adminrocks
WorkingDirectory=/opt/urvote
Environment=PATH=/opt/urvote/venv/bin
ExecStart=/opt/urvote/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable urvote
sudo systemctl start urvote
sudo systemctl status urvote
```

### 2. Nginx Configuration

Create `/etc/nginx/sites-available/urvote`:

```nginx
server {
    listen 80;
    server_name urvote.rocks www.urvote.rocks;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/urvote/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/urvote /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d urvote.rocks -d www.urvote.rocks

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Database Management

### Create Admin User

```python
# Run in Python shell
from app.database import AsyncSessionLocal
from app.models import User
from app.auth import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@urvote.rocks",
            username="admin",
            hashed_password=get_password_hash("your_admin_password"),
            is_admin=True,
            email_verified=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()

# Run the function
import asyncio
asyncio.run(create_admin())
```

### Backup Database

```bash
# Create backup
pg_dump -h localhost -U urvote_user urvote > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql -h localhost -U urvote_user urvote < backup_file.sql
```

## Monitoring and Logs

### Application Logs

```bash
# View systemd logs
sudo journalctl -u urvote -f

# View application logs
tail -f /opt/urvote/logs/app.log
```

### Database Monitoring

```bash
# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check table sizes
sudo -u postgres psql -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running: `sudo systemctl status postgresql`
   - Verify connection string in `.env`
   - Check firewall settings

2. **Permission Denied**
   - Ensure proper file ownership: `sudo chown -R adminrocks:adminrocks /opt/urvote`
   - Check upload directory permissions

3. **Port Already in Use**
   - Check what's using port 8001: `sudo netstat -tlnp | grep :8001`
   - Kill process or change port in configuration

4. **Import Errors**
   - Ensure virtual environment is activated
   - Check all dependencies are installed: `pip list`

### Performance Tuning

1. **Database Optimization**
   - Add indexes for frequently queried fields
   - Configure connection pooling
   - Regular VACUUM and ANALYZE

2. **Application Optimization**
   - Enable Redis for caching
   - Use multiple workers in production
   - Implement CDN for static files

## Security Considerations

1. **Change Default Passwords**
   - Database passwords
   - Admin user password
   - Secret keys

2. **Firewall Configuration**
   - Only expose necessary ports
   - Use fail2ban for brute force protection

3. **Regular Updates**
   - Keep system packages updated
   - Monitor security advisories
   - Regular backups

## Support

For issues and questions:
- Check the logs for error messages
- Review the FastAPI documentation
- Check the README.md for project details

## Next Steps

After setup:
1. Create your first contest
2. Test the upload and voting systems
3. Configure email notifications
4. Set up monitoring and alerts
5. Plan your launch strategy
