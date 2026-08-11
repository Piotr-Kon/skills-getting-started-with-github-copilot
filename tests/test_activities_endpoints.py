"""
Integration tests for the FastAPI activities API.
Tests use the AAA (Arrange-Act-Assert) pattern for clarity and consistency.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_correct_structure(self, client, reset_activities):
        # Arrange
        # No setup needed - activities already exist
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of each activity
        for activity_name, activity_details in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_includes_existing_participants(self, client, reset_activities):
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert expected_activity in data
        assert len(data[expected_activity]["participants"]) > 0
        assert "michael@mergington.edu" in data[expected_activity]["participants"]
    
    def test_get_activities_calculates_availability_correctly(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data[activity_name]
        
        # Assert
        expected_availability = activity["max_participants"] - len(activity["participants"])
        actual_availability = activity["max_participants"] - len(activity["participants"])
        assert expected_availability == actual_availability


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client, reset_activities):
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_adds_participant_successfully(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newtudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was added by fetching activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
    
    def test_signup_response_includes_confirmation_message(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "coder@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert "Signed up" in data["message"]
    
    def test_signup_rejects_duplicate_registration(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_to_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_increments_participant_count(self, client, reset_activities):
        # Arrange
        activity_name = "Drama Club"
        email = "actor@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_delete_removes_participant_successfully(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in data["message"]
        assert email in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
    
    def test_delete_response_includes_confirmation_message(self, client, reset_activities):
        # Arrange
        activity_name = "Drama Club"
        email = "noah@mergington.edu"  # Known participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert "Removed" in data["message"]
    
    def test_delete_nonexistent_participant_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"  # Not a participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"
    
    def test_delete_from_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_delete_decrements_participant_count(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Known participant
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
    
    def test_delete_cannot_delete_twice(self, client, reset_activities):
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        # Act - First deletion
        response1 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Attempt second deletion
        response2 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 404
        assert response2.json()["detail"] == "Participant not found in this activity"
