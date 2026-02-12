"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Join our competitive soccer team and represent Mergington High",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "james@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve your swimming technique and compete in swim meets",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop your acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 30,
            "participants": ["emily@mergington.edu", "david@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture in our creative space",
            "schedule": "Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["mia@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges at regional competitions",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "william@mergington.edu"]
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
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Soccer Team" in data
        assert "Swimming Club" in data
        assert "Drama Club" in data
    
    def test_activities_have_correct_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_activities_have_initial_participants(self, client):
        """Test that activities have their initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Soccer Team"]["participants"]
        assert "james@mergington.edu" in data["Soccer Team"]["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup for a new student"""
        response = client.post("/activities/Soccer Team/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_duplicate_student_fails(self, client):
        """Test that signing up an already registered student fails"""
        # First signup should succeed
        response1 = client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        assert response2.status_code == 400
        
        data = response2.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails"""
        response = client.post("/activities/NonExistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_with_url_encoded_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post("/activities/Soccer%20Team/signup?email=urltest@mergington.edu")
        assert response.status_code == 200
    
    def test_multiple_signups_different_students(self, client):
        """Test that multiple different students can sign up"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/Drama Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in emails:
            assert email in activities_data["Drama Club"]["participants"]


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_existing_participant_success(self, client):
        """Test successful removal of an existing participant"""
        # First add a participant
        client.post("/activities/Soccer Team/signup?email=remove-test@mergington.edu")
        
        # Then remove them
        response = client.delete("/activities/Soccer Team/participants/remove-test@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "remove-test@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "remove-test@mergington.edu" not in activities_data["Soccer Team"]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client):
        """Test that removing a non-existent participant fails"""
        response = client.delete("/activities/Soccer Team/participants/nonexistent@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_from_nonexistent_activity_fails(self, client):
        """Test that removing from a non-existent activity fails"""
        response = client.delete("/activities/NonExistent Activity/participants/test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_initial_participant(self, client):
        """Test removing one of the initial participants"""
        response = client.delete("/activities/Soccer Team/participants/alex@mergington.edu")
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Soccer Team"]["participants"]
        # But james should still be there
        assert "james@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_remove_with_url_encoded_email(self, client):
        """Test removal with URL-encoded email and activity name"""
        # Add a participant with a simple email (avoiding + which has URL encoding issues in query params)
        email = "test.special@mergington.edu"
        signup_response = client.post(f"/activities/Swimming Club/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Swimming Club"]["participants"]
        
        # Remove with URL encoding for spaces in activity name
        response = client.delete(f"/activities/Swimming%20Club/participants/{email}")
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests for common user scenarios"""
    
    def test_full_lifecycle_signup_and_remove(self, client):
        """Test the full lifecycle of signing up and removing a participant"""
        email = "lifecycle@mergington.edu"
        activity = "Chess Club"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Check participant was added
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        assert email in after_signup.json()[activity]["participants"]
        
        # Remove participant
        remove_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert remove_response.status_code == 200
        
        # Check participant was removed
        after_remove = client.get("/activities")
        assert len(after_remove.json()[activity]["participants"]) == initial_count
        assert email not in after_remove.json()[activity]["participants"]
    
    def test_multiple_activities_same_student(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multi@mergington.edu"
        activities_to_join = ["Soccer Team", "Drama Club", "Chess Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
