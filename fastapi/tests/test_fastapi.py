from uuid import uuid4
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from src.main import app
from src.db.session_model import SessionModel
from src.db.track_model import TrackModel
from src.db.registration_model import RegistrationModel

@pytest.mark.anyio
async def test_healthz_endpoint_fastapi():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/healthz")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert "checks" in data
    assert "postgres" in data["checks"]
    assert "redis" in data["checks"]

@pytest.mark.anyio
async def test_get_sessions_list_pagination(db_session):
    conf_id = uuid4()

    await db_session.execute(text(
        "INSERT INTO content.conference (id, name, slug, starts_at, ends_at, timezone) "
        "VALUES (:id, 'C', 'c', NOW(), NOW(), 'UTC')"
    ), {"id": conf_id})

    track_id = uuid4()
    db_session.add(TrackModel(id=track_id, conference_id=conf_id, name="Track 1"))
    db_session.add(SessionModel(
        id=uuid4(),
        track_id=track_id,
        title="Python Session",
        abstract="Learn Python",
        starts_at=datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc),
        ends_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        capacity=100
    ))

    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/sessions/?page=1&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)

@pytest.mark.anyio
async def test_get_session_detail_not_found():
    fake_uuid = str(uuid4())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/sessions/{fake_uuid}")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_search_sessions_endpoint(db_session):
    conf_id = uuid4()
    await db_session.execute(text(
        "INSERT INTO content.conference (id, name, slug, starts_at, ends_at, timezone) "
        "VALUES (:id, 'C', 'c', NOW(), NOW(), 'UTC')"
    ), {"id": conf_id})

    track_id = uuid4()
    db_session.add(TrackModel(id=track_id, conference_id=conf_id, name="Track 1"))
    db_session.add(SessionModel(
        id=uuid4(),
        track_id=track_id,
        title="Python Session",
        abstract="Learn Python",
        starts_at=datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc),
        ends_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        capacity=100
    ))
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/sessions/search/?query=Python")
   
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@pytest.mark.anyio
async def test_timezone_aware_filtering(db_session):
    conf_id = uuid4()
    await db_session.execute(text(
        "INSERT INTO content.conference (id, name, slug, starts_at, ends_at, timezone) "
        "VALUES (:id, 'C', 'c', NOW(), NOW(), 'UTC')"
    ), {"id": conf_id})

    track_id = uuid4()
    db_session.add(TrackModel(id=track_id, conference_id=conf_id, name="Track 1"))
    db_session.add(SessionModel(
        id=uuid4(),
        track_id=track_id,
        title="Tz Session",
        starts_at=datetime(2026, 7, 1, 2, 0, tzinfo=timezone.utc),
        ends_at=datetime(2026, 7, 1, 3, 0, tzinfo=timezone.utc),
        capacity=100
    ))
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/sessions/?day=2026-06-30&tz=America/New_York")
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1

@pytest.mark.anyio
async def test_capacity_registration_availability(db_session):
    conf_id = uuid4()

    await db_session.execute(text(
        "INSERT INTO content.conference (id, name, slug, starts_at, ends_at, timezone) "
        "VALUES (:id, 'C', 'c', NOW(), NOW(), 'UTC')"
    ), {"id": conf_id})
    
    track_id = uuid4()
    db_session.add(TrackModel(id=track_id, conference_id=conf_id, name="Track 1"))
    sess_id = uuid4()
    db_session.add(SessionModel(
        id=sess_id,
        track_id=track_id,
        title="Cap Session",
        starts_at=datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc),
        ends_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        capacity=10
    ))
    db_session.add(RegistrationModel(
        id=uuid4(),
        session_id=sess_id,
        status="confirmed"
    ))
    db_session.add(RegistrationModel(
        id=uuid4(),
        session_id=sess_id,
        status="cancelled"
    ))

    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/sessions/{sess_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["capacity"] == 10
    assert data["registered"] == 1
