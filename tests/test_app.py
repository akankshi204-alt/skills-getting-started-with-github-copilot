"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Basketball": {
            "description": "Play basketball and develop team skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create paintings, sculptures, and explore various artistic mediums",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills through competitive debate",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["rachel@mergington.edu", "david@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM concepts",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["nina@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear current activities
    activities.clear()
    # Restore original state
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert len(data) == 9
    
    def test_get_activities_has_required_fields(self, client):
        """Test that activities contain all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_list(self, client):
        """Test that participants are returned as a list"""
        response = client.get("/activities")
        data = response.json()
        
        assert isinstance(data["Basketball"]["participants"], list)
        assert "james@mergington.edu" in data["Basketball"]["participants"]


class TestSignUp:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball"]["participants"]
    
    def test_signup_duplicate_email(self, client):
        """Test signup fails for duplicate email"""
        response = client.post(
            "/activities/Basketball/signup?email=james@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup fails for nonexistent activity"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_different_activities(self, client):
        """Test student can signup for multiple different activities"""
        student_email = "multiactivity@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            f"/activities/Basketball/signup?email={student_email}"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            f"/activities/Tennis%20Club/signup?email={student_email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert student_email in activities_data["Basketball"]["participants"]
        assert student_email in activities_data["Tennis Club"]["participants"]


class TestUnregister:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successfully unregistering from an activity"""
        response = client.delete(
            "/activities/Basketball/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "james@mergington.edu" in data["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "james@mergington.edu" not in activities_data["Basketball"]["participants"]
    
    def test_unregister_not_registered(self, client):
        """Test unregister fails when student is not registered"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister fails for nonexistent activity"""
        response = client.delete(
            "/activities/NonexistentActivity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_after_signup(self, client):
        """Test unregister after signing up"""
        student_email = "signup_unregister@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Basketball/signup?email={student_email}"
        )
        assert signup_response.status_code == 200
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Basketball/unregister?email={student_email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert student_email not in activities_data["Basketball"]["participants"]


class TestRoot:
    """Test suite for root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
