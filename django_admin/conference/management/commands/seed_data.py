import random
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from conference.models import Conference, Registration, Session, Speaker, Track
SessionSpeaker = Session.speakers.through

TRACK_NAMES = ["Backend", "Frontend", "DevOps", "Security", "Data Science"]

def session_start(index):
    return datetime(2026, 7, 1 + (index % 5), 9 + (index // 5) % 8, tzinfo=timezone.utc)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if Conference.objects.filter(slug="djangocon-2026").exists():
            return

        conference = Conference.objects.create(
            name="DjangoCon 2026",
            slug="djangocon-2026",
            starts_at=datetime(2026, 7, 1, 9, tzinfo=timezone.utc),
            ends_at=datetime(2026, 7, 5, 18, tzinfo=timezone.utc),
            timezone="UTC",
        )

        tracks = [
            Track.objects.create(conference=conference, name=name)
            for name in TRACK_NAMES
        ]
        speakers = [
            Speaker.objects.create(name=f"Speaker {i + 1}", affiliation="Tech Company")
            for i in range(10)
        ]

        sessions = Session.objects.bulk_create([
            Session(
                track=tracks[i % len(tracks)],
                title=f"Session {i + 1}",
                abstract=f"Abstract for session {i + 1}",
                starts_at=session_start(i),
                ends_at=session_start(i) + timedelta(minutes=45),
                capacity=random.randint(20, 100),
            )
            for i in range(300)
        ])

        SessionSpeaker.objects.bulk_create([
            SessionSpeaker(session=sessions[i], speaker=speakers[i % len(speakers)])
            for i in range(len(sessions))
        ])

        Registration.objects.bulk_create([
            Registration(
                session=sessions[i % len(sessions)],
                user_email=f"user{i + 1}@example.com",
                status=random.choice(["confirmed", "waitlist", "cancelled"]),
            )
            for i in range(500)
        ])
