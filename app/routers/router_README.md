# Routers Directory README

This README will document all routers in the UrVote project as they are completed and refined.

## Purpose
This directory contains all FastAPI routers, organized by feature or function. Each router handles a specific set of endpoints, either for API (JSON) or frontend (HTML template) purposes.

## Routers Overview

- **static_pages.py**: Static and informational pages (home, about, contact, FAQ, etc.)
- **voting.py**: Voting API endpoints and (optionally) voting-related HTML pages
- **voter.py**: Voter-facing HTML pages 
- **songs.py**: Handles all song-related actions:
    - **POST `/songs/upload`**: Upload a new song (with file validation and DigitalOcean Spaces integration)
    - **GET `/songs/`**: List songs, with optional approval filtering and pagination
    - **GET `/songs/{song_id}`**: Get details for a specific song
    - **POST `/songs/{song_id}/approve`**: Admin-only, approve or reject a song
    - **GET `/songs/pending/approval`**: Admin-only, list songs pending approval
- **songboards.py**: Songboard/contest-related endpoints
- **signup.py**: User signup and onboarding
- **submitter.py**: Song submitter-related endpoints
- **auth.py**: Authentication and user management

## How to Use
- As you complete or refactor a router, add a summary and key endpoints here.
- Use this README to keep track of the purpose and structure of each router.

---

*Update this file as your routing structure evolves!*
