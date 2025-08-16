import asyncio
import random
from app.models import Board, Song, User
from app.database import AsyncSessionLocal
from sqlalchemy import select

BOARD_TITLES = [
    "AI Hits 2024", "Summer Jams", "Indie Showcase", "Viral TikTok Sounds"
]
ARTISTS = [
    "DJ Neural", "Synth Sage", "RoboVox", "AI Melody", "ByteBeats", "Code Composer"
]
SONG_TITLES = [
    "Electric Dreams", "Binary Love", "Algorithmic Heart", "Neural Nights",
    "Quantum Groove", "Digital Sunrise", "Pixelated Soul", "Synthwave Sky"
]

# bcrypt hash for 'password123' (for demo only)
DEMO_HASHED_PASSWORD = "$2b$12$KIXQ4Q1rQ1rQ1rQ1rQ1rQeQ1rQ1rQ1rQ1rQ1rQ1rQ1rQ1rQ1rQ"

async def seed():
    async with AsyncSessionLocal() as session:
        # Create boards (only if not exists)
        boards = []
        for title in BOARD_TITLES:
            slug = title.lower().replace(" ", "-")
            existing = (await session.execute(
                select(Board).where(Board.slug == slug)
            )).scalar_one_or_none()
            if existing:
                boards.append(existing)
                continue
            board = Board(title=title, slug=slug)
            session.add(board)
            boards.append(board)
        await session.commit()
        for board in boards:
            await session.refresh(board)

        # Create users (only if not exists)
        users = []
        for i in range(10):
            email = f"user{i}@demo.com"
            username = f"user{i}"
            existing = (await session.execute(
                select(User).where(User.email == email)
            )).scalar_one_or_none()
            if existing:
                users.append(existing)
                continue
            user = User(
                email=email,
                username=username,
                hashed_password=DEMO_HASHED_PASSWORD
            )
            session.add(user)
            users.append(user)
        await session.commit()
        for user in users:
            await session.refresh(user)

        # Create songs
        songs = []
        for board in boards:
            for i in range(5):
                song = Song(
                    title=random.choice(SONG_TITLES) + f" #{i+1}",
                    artist_name=random.choice(ARTISTS),
                    board_id=board.id,  # <-- Correct usage
                    url=f"https://cdn.example.com/audio/{random.randint(1000,9999)}.mp3",
                    social_link="https://twitter.com/demo_artist",
                    votes=random.randint(0, 100)
                )
                session.add(song)
                songs.append(song)
        await session.commit()
        for song in songs:
            await session.refresh(song)

    print("Demo data seeded!")

if __name__ == "__main__":
    asyncio.run(seed())