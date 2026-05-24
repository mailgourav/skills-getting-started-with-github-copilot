import pytest


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        # Activities are already set up in the fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_includes_required_fields(self, client):
        # Arrange
        # Activities are already set up in the fixture
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_get_activities_shows_correct_participants(self, client):
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert activities["Chess Club"]["participants"] == expected_participants


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_successfully(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    def test_signup_duplicate_student_rejected(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_multiple_new_students(self, client, fresh_activities):
        # Arrange
        activity_name = "Programming Class"
        new_emails = ["alice@mergington.edu", "bob@mergington.edu"]
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={new_emails[0]}"
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={new_emails[1]}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert new_emails[0] in fresh_activities[activity_name]["participants"]
        assert new_emails[1] in fresh_activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Test DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_successfully(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in fresh_activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"
    
    def test_unregister_multiple_participants(self, client, fresh_activities):
        # Arrange
        activity_name = "Gym Class"
        emails = ["john@mergington.edu", "olivia@mergington.edu"]
        
        # Act
        response1 = client.delete(
            f"/activities/{activity_name}/unregister?email={emails[0]}"
        )
        response2 = client.delete(
            f"/activities/{activity_name}/unregister?email={emails[1]}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == 0


class TestSignupAndUnregisterFlow:
    """Test signup and unregister working together"""
    
    def test_signup_then_unregister(self, client, fresh_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert signup
        assert signup_response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert unregister
        assert unregister_response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
    
    def test_signup_unregister_then_signup_again(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act - First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Act - Sign up again
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
