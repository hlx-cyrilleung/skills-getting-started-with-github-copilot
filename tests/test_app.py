"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    from src.app import activities
    
    # Store original state
    original_activities = {
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competition",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis": {
            "description": "Learn tennis techniques and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills through debate",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and experiments",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and improve acting skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
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
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Tennis" in data
        assert len(data) == 9
    
    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)
    
    def test_initial_participants(self, client):
        """Test that initial participants are loaded correctly"""
        response = client.get("/activities")
        data = response.json()
        
        assert "james@mergington.edu" in data["Basketball"]["participants"]
        assert "noah@mergington.edu" in data["Science Olympiad"]["participants"]
        assert "isabella@mergington.edu" in data["Science Olympiad"]["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Basketball/signup?email=james@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test multiple students can sign up for the same activity"""
        # First signup
        response1 = client.post(
            "/activities/Basketball/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(
            "/activities/Basketball/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()["Basketball"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First verify the participant is registered
        activities_response = client.get("/activities")
        assert "james@mergington.edu" in activities_response.json()["Basketball"]["participants"]
        
        # Unregister
        response = client.post(
            "/activities/Basketball/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert "james@mergington.edu" not in activities_response.json()["Basketball"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/NonExistent/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        response = client.post(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_multiple_times(self, client):
        """Test that unregister can only happen once"""
        # First unregister
        response1 = client.post(
            "/activities/Basketball/unregister?email=james@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.post(
            "/activities/Basketball/unregister?email=james@mergington.edu"
        )
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
