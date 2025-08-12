# 🎵 UrVote.Rocks - AI Music Contest Platform

## 🌟 Overview

**UrVote.Rocks** is a B2B SaaS platform that enables companies to create and manage AI-generated music contests. The platform combines cutting-edge AI music generation with democratic voting systems, allowing brands to engage their audiences through music competitions.

## 🏗️ Platform Architecture

### **Business Model**
- **B2B SaaS**: Companies pay monthly fees to use the contest platform
- **White-label solution**: Each client gets their own branded contest space
- **Revenue streams**: Platform subscriptions + potential voter micro-payments

### **Core Components**
- **Contest Management**: Create, configure, and manage music contests
- **User Management**: Artist registration and profile management
- **Audio Handling**: MP3 upload, storage, and streaming
- **Voting System**: Democratic voting with fraud prevention
- **Analytics**: Contest performance and engagement metrics

## 📁 File Structure

### **Audio File Organization**
```
/opt/urvote/app/static/audio/
├── payportpro/                    # Client folder
│   ├── patriotic-2024/           # Contest folder
│   │   ├── sound of chi/         # User folder
│   │   │   ├── Maga Maga 401.mp3
│   │   │   └── Patriotic Anthem.mp3
│   │   ├── soundofchi2/          # Another user
│   │   │   └── Maga 501.mp3
│   │   └── soundofchi3/          # Third user
│   │       └── Maga 502.mp3
│   └── future-contest/            # Future contest
│       └── new_artist/
│           └── New Song.mp3
└── client2/                       # Future client
    └── contest-name/
        └── artist_name/
            └── song.mp3
```

### **Why This Structure?**
- **Client isolation**: Each client gets their own space
- **Contest organization**: Songs grouped by contest
- **User separation**: Each artist has their own folder
- **Scalability**: Easy to add new clients and contests
- **Management**: Simple to archive old contests

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- PostgreSQL 12+
- FastAPI
- Docker (optional)

### **Installation**
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd urvote
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API keys
   ```

5. **Set up database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

## 🎯 Platform Features

### **For Contest Sponsors (Companies)**
- **Contest Creation**: Set themes, rules, and timeframes
- **Branding**: Custom logos, colors, and domain options
- **Moderation**: Content approval and management tools
- **Analytics**: Real-time contest performance metrics
- **User Management**: Contestant and voter oversight

### **For Contest Participants (Artists)**
- **Song Submission**: Upload AI-generated music files
- **Profile Management**: Artist bio, website, social links
- **Contest Participation**: Submit to multiple contests
- **Community Engagement**: Connect with other artists

### **For Voters**
- **Song Discovery**: Browse and listen to contest entries
- **Voting System**: Fair, transparent voting process
- **Community Participation**: Engage with AI music community
- **Premium Features**: Enhanced voting options (future)

## 💰 Pricing Tiers

### **Starter - $199/month**
- 1 active contest at a time
- Up to 50 song submissions
- Up to 2,500 voters
- Basic contest branding
- Standard voting system
- Basic moderation tools
- Basic analytics

### **Pro - $499/month**
- Up to 5 active contests
- Up to 250 submissions per contest
- Up to 20,000 voters
- Full custom branding
- Advanced voting options
- Advanced moderation
- Enhanced analytics
- Social sharing tools

### **Enterprise - Custom Pricing**
- Unlimited active contests
- Unlimited submissions & voters
- White-label platform
- Custom voting rules
- Premium moderation suite
- Full analytics suite
- Dedicated account manager
- Priority support & SLA

## 🔧 API Endpoints

### **Songs**
- `GET /api/songs/` - List approved songs
- `POST /api/songs/upload` - Upload new song
- `GET /api/songs/{song_id}` - Get song details
- `POST /api/songs/{song_id}/approve` - Approve/reject song

### **Voting**
- `POST /api/voting/vote` - Cast a vote
- `GET /api/voting/leaderboard` - Get contest leaderboard
- `GET /api/voting/stats` - Get voting statistics
- `GET /api/voting/my-votes` - Get user's voting history

### **Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

## 📊 Database Schema

### **Key Tables**
- **users**: User accounts and profiles
- **songs**: Song submissions and metadata
- **contests**: Contest configuration and rules
- **votes**: Voting records and analytics
- **clients**: Client companies and settings

### **User Profile Fields**
- `artist_name`: Display name for the artist
- `bio`: Artist biography
- `website`: Artist website URL
- `social_links`: JSON object with social media links
- `profile_image`: Profile picture URL
- `is_contestant`: Can submit songs
- `is_voter`: Can vote in contests
- `location`: Artist location
- `genre`: Primary music genre
- `years_active`: Years making music

## 🎵 Contest Workflow

### **1. Contest Setup**
- Client creates contest with theme and rules
- Platform generates contest space and branding
- Contest opens for submissions

### **2. Song Submission**
- Artists register and create profiles
- Artists upload AI-generated music files
- Songs go through moderation process
- Approved songs appear in contest

### **3. Voting Phase**
- Contest opens for public voting
- Users listen to songs and cast votes
- Real-time leaderboard updates
- Fraud prevention measures active

### **4. Contest Results**
- Voting period ends
- Final results calculated and displayed
- Winners announced and recognized
- Contest archived for future reference

## 🔒 Security & Moderation

### **Content Moderation**
- **Automated filtering**: Profanity and content scanning
- **Human review**: Manual approval for contest entries
- **Copyright protection**: Flagging potential copyright issues
- **Community guidelines**: Clear rules for submissions

### **Voting Security**
- **Rate limiting**: One vote per song per day per user
- **IP tracking**: Geographic voting analytics
- **User verification**: Email verification required
- **Fraud detection**: Suspicious voting pattern detection

## 🚀 Deployment

### **Production Setup**
1. **Environment variables**
   - Database connection strings
   - API keys and secrets
   - File storage paths
   - Email service configuration

2. **Database optimization**
   - Indexes on frequently queried fields
   - Connection pooling
   - Regular backups

3. **File storage**
   - Audio file organization by client/contest/user
   - CDN integration for fast delivery
   - Backup and archival strategies

4. **Monitoring**
   - Application performance monitoring
   - Error tracking and alerting
   - User analytics and insights

## 📈 Scaling Strategy

### **Short Term (0-6 months)**
- Launch with PayPortPro contest
- Build user community
- Refine platform features
- Establish pricing model

### **Medium Term (6-18 months)**
- Add 5-10 new clients
- Expand contest types
- Implement premium voting features
- Add mobile app

### **Long Term (18+ months)**
- International expansion
- Advanced AI integration
- White-label partnerships
- Enterprise features

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

### **Code Standards**
- Follow PEP 8 Python style guide
- Add type hints to functions
- Include docstrings for all functions
- Write tests for new features

## 📞 Support

### **Technical Support**
- **Email**: support@urvote.rocks
- **Documentation**: [docs.urvote.rocks](https://docs.urvote.rocks)
- **Issues**: GitHub Issues page

### **Business Inquiries**
- **Sales**: sales@urvote.rocks
- **Partnerships**: partnerships@urvote.rocks
- **General**: hello@urvote.rocks

## 📄 License

This project is proprietary software. All rights reserved.

---

**UrVote.Rocks** - The Future of AI Music Contests 🎵✨
