import pytest
from datetime import datetime, timezone
from project2 import app
from database import db
from models import Snapshot
 
 
@pytest.fixture
def test_client():
    # Use an in-memory database for tests — never touches weather.db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
 
    with app.app_context():
        db.create_all()          # create tables in the test database
        yield app.test_client()  # run the test
        db.drop_all()            # wipe everything after the test
 
 
@pytest.fixture
def sample_snapshot(test_client):
    """Insert one row we can query against."""
    with app.app_context():
        row = Snapshot(
            fetched_at        = datetime.now(timezone.utc),
            city              = 'Toronto',
            temperature_c     = 14.2,
            wind_speed_kmh    = 18.5,
            weather_code      = 3,
            pm10              = 12.0,
            pm2_5             = 6.1,
            air_quality_index = 15,
        )
        db.session.add(row)
        db.session.commit()
    return test_client
 
 
def test_history_empty_returns_empty_list(test_client):
    response = test_client.get('/history')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 0
 
 
def test_history_returns_saved_row(sample_snapshot):
    response = sample_snapshot.get('/history')
    data = response.get_json()
    assert data['count'] == 1
    assert data['data'][0]['city'] == 'Toronto'
 
 
def test_city_history_unknown_city_returns_404(test_client):
    response = test_client.get('/history/atlantis')
    assert response.status_code == 404
 
 
def test_summary_calculates_average(sample_snapshot):
    response = sample_snapshot.get('/history/toronto/summary')
    data = response.get_json()
    assert data['temperature_c']['avg'] == 14.2
    assert data['total_readings'] == 1
