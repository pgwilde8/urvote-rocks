# **UrVote.Rocks – Contest Platform README**

## **Overview**

UrVote.Rocks is a **SaaS contest platform** that allows brands, events, and creators to run public voting competitions with:

* File uploads (music, video, images, etc.)
* Public leaderboards
* Social sharing hooks
* Fraud-protected voting
* Admin moderation

**First Client & Case Study:**
PayPortPro, a fintech platform, will be the first user of UrVote.Rocks to host the **“Best Pro-American AI Song” Contest**. This high-profile launch will serve as a **public showcase** for the SaaS, generating proof, media attention, and leads for future UrVote.Rocks clients.

---

## **Project Goals**

1. **Deliver MVP in Time for PayPortPro’s Contest**

   * Contest must launch publicly with full upload → approve → vote → leaderboard → share loop.
2. **Create a Reusable SaaS Platform**

   * Features must be generic enough to run *any* contest after the PayPortPro launch.
3. **Capture Marketing Leads**

   * All voting flows should collect voter email/SMS for client use.
4. **Demonstrate Virality**

   * Built-in social sharing tools so contestants promote their own entries, driving traffic back.

---

## **MVP Features**

### **1. Submission Flow**

* User registration (email verification)
* Upload file (MP3/WAV for this contest) OR submit external link (YouTube/SoundCloud)
* Metadata: title, genre, AI tools used, short description, license choice:

  * **Stream only**
  * **Creative Commons (CC BY-NC 4.0)** for download/remix
* Store files in **DigitalOcean Spaces** (S3-compatible)
* Admin moderation queue (approve/reject)

### **2. Voting**

* Public voting for approved entries
* Limit: 1 vote per user per song per day
* Email verification required
* Fraud prevention:

  * reCAPTCHA v3
  * IP/device fingerprint
  * Disposable email domain blocking
* GeoIP tagging of votes:

  * **USA votes** (eligible for contest prize)
  * **Global votes** (for “People’s Choice” recognition)

### **3. Leaderboards**

* Global leaderboard (all votes)
* USA-only leaderboard (filtered)
* Sorting by vote count, date added
* Song detail pages with:

  * Audio player
  * Metadata
  * License badge
  * Share buttons (Facebook, TikTok, IG, Twitter/X)

### **4. Social Sharing Hooks**

* After voting:

  * “Thanks for voting — share this song” page
  * Pre-filled captions and hashtags (#UrVoteRocks, #BestProAmericanSong)
* Open Graph metadata for previews when links are shared

### **5. Admin Tools**

* Approve/reject entries
* Track daily votes per entry
* Export voter email/SMS list for marketing
* Flag suspicious votes for review

---

## **Tech Stack**

* **Backend:** FastAPI (Python 3.11+), async SQLAlchemy
* **Database:** PostgreSQL 14+ (DigitalOcean Managed DB)
* **Frontend:** Jinja2 templates + TailwindCSS
* **Storage:** DigitalOcean Spaces (S3-compatible)
* **Cache/Queue:** Redis (for rate limiting, moderation queues)
* **Deployment:** Uvicorn + Nginx + systemd
* **Domain:** urvote.rocks (SSL via Let’s Encrypt)
* **Version Control:** GitHub (private repo)

---

## **Development Rules**

* **No coding on production** — staging server first, then deploy to live
* **Branch naming:** `feature/voting`, `feature/uploads`, `bugfix/leaderboard`, etc.
* **Weekly milestones** — each ends with a demo on staging
* **All code pushed to GitHub repo** — you own the repo
* **Separate `.env`** for staging & production — never commit secrets
* Use **fake API keys** in staging (Stripe test, Twilio sandbox, etc.)

---

## **Timeline (First 2 Weeks)**

### **Week 1**

* Set up repo, staging server, and base FastAPI app
* Implement user registration + email verification
* Build song submission form + S3 upload
* Create admin panel for approvals

### **Week 2**

* Build voting system with fraud checks
* Build basic leaderboards
* Add share page after voting
* Add GeoIP tagging to votes

---

## **Deliverables for PayPortPro Launch**

By launch date, **the staging build must support**:

1. New user signup → email verify
2. Upload song → admin approves
3. Public voting → votes stored & counted
4. View leaderboard → accurate & updated
5. Share page → pre-filled captions, hashtag, and link

---

## **Marketing Notes**

* Every page must have **“Powered by UrVote.Rocks”** in footer
* All shareable links lead back to **UrVote.Rocks** domain
* TikTok/IG content seeded with at least 10 initial entries
* Collect voter contact info for PayPortPro AND for UrVote.Rocks case study marketing

---

## **Post-PayPortPro Launch Plan**

1. Use contest results (entries, votes, traffic) as **public case study**
2. Approach:

   * Music festivals
   * Nonprofits
   * Radio stations
   * Brand marketers
3. Offer **launch discount** to first 10 SaaS clients

1. Board Owners (Platform Clients)
Who they are: Businesses/organizations that create and manage media boards
Authentication needs:
Account required: Yes, full account needed
Registration flow: Email + password + business verification
Access level: Full platform access, board management, analytics
Session management: Long-lived sessions, "remember me" functionality
Security: High - they control boards and have billing access
Proposed flow:
2. Content Creators/Uploaders (Contestants)
Who they are: Artists, musicians, videographers who submit content to boards
Authentication needs:
Account required: Yes, but simplified
Registration flow: Email + password + basic profile (optional social links)
Access level: Upload content, manage their submissions, view their stats
Session management: Standard sessions
Security: Medium - they can upload content but limited scope
Proposed flow:
3. Voters (Public Participants)
Who they are: General public who vote on content
Authentication needs:
Account required: No (as you mentioned for user acquisition)
Identification: Email + name only (already implemented)
Access level: Vote, view content, share
Session management: None - stateless voting
Security: Low - limited to voting with fraud prevention
