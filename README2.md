# 🎵 UrVote.Rocks - Modern Contest Platform

> **A SaaS platform for running viral media contests with anonymous voting and fraud prevention**

## 🚀 Overview

UrVote.Rocks is a **modern SaaS contest platform** that enables businesses, events, and creators to run engaging media competitions with robust fraud prevention and viral sharing capabilities. The platform supports multiple content types (music, video, visuals) and features anonymous voting to maximize user acquisition.

### 🎯 Mission
Democratize contest hosting by providing an easy-to-use platform that combines viral sharing mechanics with enterprise-grade fraud prevention.

---

## 👥 User Types & Authentication

### 1. 🏢 **Board Owners** (Platform Clients)
**Who:** Businesses, organizations, and event organizers who create and manage contest boards

**Authentication:**
- ✅ **Full account required** with email verification
- 🔐 **High security** - controls boards and billing
- 📊 **Full platform access** - analytics, moderation, board management
- ⏰ **Long-lived sessions** with "remember me" functionality

**Capabilities:**
- Create and customize media boards with themes
- Set contest rules and voting parameters
- Moderate content submissions
- Access detailed analytics and voter data
- Manage billing and subscriptions

### 2. 🎨 **Content Creators** (Contestants)
**Who:** Artists, musicians, videographers, and creators who submit content to contests

**Authentication:**
- ✅ **Simplified account** with email verification
- 🔐 **Medium security** - limited to content management
- 📝 **Profile management** - basic info and social links
- ⏰ **Standard sessions**

**Capabilities:**
- Upload content (music, video, visuals)
- Manage their submissions and track performance
- View personal statistics and leaderboard position
- Share their content across social platforms

### 3. 🗳️ **Voters** (Public Participants)
**Who:** General public who participate in voting

**Authentication:**
- ❌ **No account required** (for maximum user acquisition)
- 📧 **Email + name only** for identification
- 🔐 **Low security** - limited to voting with fraud prevention
- ⚡ **Stateless voting** - no session management

**Capabilities:**
- Vote on approved content anonymously
- Share content and contests
- View leaderboards and contest results

---

## ✨ Key Features

### 🎵 **Multi-Media Support**
- **Music:** MP3, WAV, M4A support with audio players
- **Video:** MP4, MOV, AVI with embedded players
- **Visuals:** JPG, PNG, GIF with gallery views

### 🗳️ **Anonymous Voting System**
- **No registration required** for voters
- **Email verification** for vote validation
- **Daily vote limits** per email address
- **Fraud prevention:**
  - reCAPTCHA v3 integration
  - IP/device fingerprinting
  - Disposable email blocking
  - Suspicious activity detection
  - Rate limiting and GeoIP tagging

### 📊 **Real-Time Leaderboards**
- Live vote counting and ranking
- Multiple sorting options (votes, date, popularity)
- Content detail pages with metadata
- Social sharing integration

### 🎨 **Customizable Board Themes**
- Pre-built themes (sunset, ocean, neon, etc.)
- Custom branding and colors
- Business information integration
- Social media link management

### 🔒 **Admin Moderation**
- Content approval workflow
- Suspicious vote flagging
- User management and analytics
- Export capabilities for voter data

---

## 🏗️ Technical Architecture

### **Backend Stack**
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 14+ with async SQLAlchemy
- **ORM:** SQLAlchemy with Alembic migrations
- **Authentication:** JWT tokens with role-based access
- **File Storage:** DigitalOcean Spaces (S3-compatible)
- **Caching:** Redis for rate limiting and sessions
- **Server:** Uvicorn with Nginx reverse proxy

### **Frontend Stack**
- **Templates:** Jinja2 with TailwindCSS
- **Styling:** TailwindCSS for responsive design
- **JavaScript:** Vanilla JS with modern ES6+
- **Icons:** Heroicons and custom SVG icons

### **Infrastructure**
- **Deployment:** systemd service management
- **SSL:** Let's Encrypt certificates
- **Domain:** urvote.rocks
- **Monitoring:** Built-in logging and error tracking

---

## 📁 Project Structure

```
/opt/urvote/
├── app/
│   ├── models.py          # SQLAlchemy database models
│   ├── config.py          # Pydantic settings configuration
│   ├── main.py            # FastAPI application entry point
│   ├── database.py        # Database connection and session management
│   ├── routers/           # API route handlers
│   │   ├── boards.py      # Board management and content uploads
│   │   ├── voting.py      # Voting system and leaderboards
│   │   └── admin.py       # Admin panel and moderation
│   ├── utils/             # Utility functions
│   │   └── main.py        # File handling and fraud prevention
│   └── templates/         # Jinja2 HTML templates
│       ├── get-media-board.html
│       ├── templates.html
│       └── vote_form.html
├── uploads/               # File storage with organized structure
│   ├── music/
│   ├── video/
│   └── visuals/
├── alembic/              # Database migrations
├── .env                  # Environment configuration
└── requirements.txt      # Python dependencies
```

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- DigitalOcean Spaces account (or AWS S3)

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd urvote
   ```

2. **Create virtual environment**
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
   cp env.example .env
   # Edit .env with your database and API credentials
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### **Production Deployment**

1. **Configure systemd service**
   ```bash
   sudo systemctl enable urvote
   sudo systemctl start urvote
   ```

2. **Set up Nginx reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name urvote.rocks;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 🎯 Current Status

### ✅ **Completed Features**
- [x] Multi-media upload system with organized directory structure
- [x] Anonymous voting with fraud prevention
- [x] Real-time leaderboards and content display
- [x] Board creation and theme customization
- [x] Admin moderation panel
- [x] Free board creation mode for user acquisition
- [x] Database schema with proper relationships
- [x] File upload validation and security

### 🚧 **In Development**
- [ ] User authentication system for Board Owners and Creators
- [ ] Role-based access control
- [ ] Enhanced fraud prevention algorithms
- [ ] Social media integration improvements

### 📋 **Planned Features**
- [ ] Stripe payment integration for premium boards
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] API for third-party integrations
- [ ] Multi-language support

---

## 🌍 Launch Strategy

### **Phase 1: Philippines Launch (1000 Users)**
- **Goal:** Attract angel investors with user traction
- **Strategy:** Free board creation to maximize adoption
- **Target:** Music and video contests in Philippines market
- **Timeline:** Q1 2024

### **Phase 2: Southeast Asia Expansion**
- **Goal:** Scale to 10,000+ users
- **Strategy:** Paid premium features, enterprise clients
- **Target:** Regional brands and events
- **Timeline:** Q2-Q3 2024

### **Phase 3: Global Platform**
- **Goal:** International SaaS platform
- **Strategy:** Full monetization, advanced features
- **Target:** Global brands, agencies, event organizers
- **Timeline:** Q4 2024+

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 📞 Support

- **Documentation:** [docs.urvote.rocks](https://docs.urvote.rocks)
- **Issues:** [GitHub Issues](https://github.com/urvote/urvote/issues)
- **Email:** support@urvote.rocks
- **Discord:** [Join our community](https://discord.gg/urvote)



<div align="center">

**Made with ❤️ for creators, by creators**

[Website](https://urvote.rocks) • [Documentation](https://docs.urvote.rocks) • [Twitter](https://twitter.com/urvote) • [LinkedIn](https://linkedin.com/company/urvote)

</div>
