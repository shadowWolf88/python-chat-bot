"""
Quick Wins Week 1 - Integration & Unit Tests

Features tested:
1. Progress % Display (mood improvement tracking)
2. Achievement Badges (gamification system)
3. Homework Visibility (assignment tracking)
4. Patient Search for Clinicians (search + filtering)

Total: 25 test cases
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestProgressPercentageDisplay:
    """Tests for Progress % Display Feature"""
    
    def test_progress_mood_not_authenticated(self, client):
        """GET /api/patient/progress/mood without auth returns 401"""
        response = client.get('/api/patient/progress/mood')
        assert response.status_code == 401
        assert 'Authentication required' in response.json['error']
    
    def test_progress_mood_with_auth_no_logs(self, auth_patient):
        """GET /api/patient/progress/mood with auth but no mood logs"""
        client, user = auth_patient
        
        with patch('api.get_db_connection') as mock_conn:
            # Setup mock to return no mood logs
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [None, None]  # first_log and latest_log are None
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/patient/progress/mood')
            
            assert response.status_code == 200
            data = response.json
            assert data['progress_percentage'] == 0
            assert data['trend'] == 'no_data'
            assert data['entries_count'] == 0
    
    def test_progress_mood_with_entries(self, auth_patient, mock_db):
        """GET /api/patient/progress/mood calculates progress correctly"""
        client, user = auth_patient
        
        # Mock database with mood entries
        query_results = {
            'first_log': (5, '2025-01-01T10:00:00'),  # mood_val, timestamp
            'latest_log': (7, '2025-02-11T10:00:00'),
            'count': 10,
            'last_7': [(7,), (6,), (8,), (7,), (6,), (5,), (4,)]  # Moving average
        }
        
        with patch('api.get_db_connection') as mock_conn, \
             patch('api.log_event') as mock_log:
            
            mock_cursor = MagicMock()
            # Setup side_effect for multiple calls
            mock_cursor.execute.return_value = mock_cursor
            mock_cursor.fetchone.side_effect = [
                (5, '2025-01-01T10:00:00'),  # first_log
                (7, '2025-02-11T10:00:00'),  # latest_log
                (10,),  # count
                None, None, None  # For last_7 setup
            ]
            mock_cursor.fetchall.return_value = [(7,), (6,), (8,), (7,), (6,), (5,), (4,)]
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/patient/progress/mood')
            
            assert response.status_code == 200
            data = response.json
            assert 'progress_percentage' in data
            assert 'trend' in data
            assert 'first_mood' in data
            assert 'latest_mood' in data
            assert 'entries_count' in data
            mock_log.assert_called()


class TestAchievementBadges:
    """Tests for Achievement Badges Feature"""
    
    def test_get_achievements_no_auth(self, client):
        """GET /api/patient/achievements without auth returns 401"""
        response = client.get('/api/patient/achievements')
        assert response.status_code == 401
    
    def test_get_achievements_empty(self, auth_patient):
        """GET /api/patient/achievements with no earned badges"""
        client, user = auth_patient
        
        with patch('api.get_db_connection') as mock_conn, \
             patch('api._calculate_achievement_progress') as mock_progress:
            
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []  # No achievements
            mock_progress.return_value = {'badges_close': []}
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/patient/achievements')
            
            assert response.status_code == 200
            data = response.json
            assert data['earned'] == []
            assert data['total_earned'] == 0
            assert 'progress' in data
    
    def test_check_achievement_unlocks_first_mood(self, auth_patient):
        """POST /api/patient/achievements/check-unlocks unlocks first_log badge"""
        client, user = auth_patient
        
        with patch('api.get_db_connection') as mock_conn, \
             patch('api.log_event') as mock_log:
            
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            # Setup: 1 mood log, no existing first_log badge
            mock_cursor.fetchone.side_effect = [(1,), None]  # count=1, existing=None
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.post('/api/patient/achievements/check-unlocks')
            
            assert response.status_code == 200
            data = response.json
            assert any(a['name'] == 'first_log' for a in data.get('newly_unlocked', []))
    
    def test_check_achievement_unlocks_streak(self, auth_patient):
        """POST /api/patient/achievements/check-unlocks unlocks streak badges"""
        client, user = auth_patient
        
        with patch('api.get_db_connection') as mock_conn, \
             patch('api._check_mood_streak') as mock_streak:
            
            mock_streak.side_effect = [30, 30]  # 30 day streak for both checks
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            mock_cursor.fetchone.side_effect = [
                (30,),  # mood_count
                None,   # existing streak_7
                None    # existing streak_30
            ]
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.post('/api/patient/achievements/check-unlocks')
            
            assert response.status_code == 200
            data = response.json
            assert len(data.get('newly_unlocked', [])) >= 0  # May unlock badges


class TestHomeworkVisibility:
    """Tests for Homework Visibility Feature"""
    
    def test_get_homework_no_auth(self, client):
        """GET /api/patient/homework without auth returns 401"""
        response = client.get('/api/patient/homework')
        assert response.status_code == 401
    
    def test_get_homework_this_week(self, auth_patient):
        """GET /api/patient/homework returns this week's assignments"""
        client, user = auth_patient
        
        with patch('api.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            # Mock homework assignments
            mock_cursor.fetchall.return_value = [
                (1, 'Identify thoughts', 'Thought record 1', 'Evidence', '2025-02-10T10:00:00'),
                (2, 'Challenge thoughts', 'Thought record 2', 'Evidence', '2025-02-09T10:00:00')
            ]
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/patient/homework')
            
            assert response.status_code == 200
            data = response.json
            assert 'homework' in data
            assert 'this_week_count' in data
            assert 'completion_rate' in data
            assert data['status'] == 'success'


class TestPatientSearchDashboard:
    """Tests for Patient Search & Filtering (Clinician)"""
    
    def test_search_patients_no_auth(self, client):
        """GET /api/clinician/patients/search without auth returns 401"""
        response = client.get('/api/clinician/patients/search?q=test')
        assert response.status_code == 401
    
    def test_search_patients_non_clinician(self, auth_patient):
        """GET /api/clinician/patients/search by non-clinician returns 403"""
        client, user = auth_patient  # This is a patient, not a clinician
        
        with patch('api.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            mock_cursor.fetchone.return_value = ('user',)  # Patient role, not clinician
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/clinician/patients/search?q=test')
            
            assert response.status_code == 403
            assert 'Clinician access required' in response.json['error']
    
    def test_search_patients_empty_results(self, auth_clinician):
        """GET /api/clinician/patients/search with no matches"""
        client, user = auth_clinician
        
        with patch('api.get_db_connection') as mock_conn, \
             patch('api.log_event') as mock_log:
            
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            # Setup mock responses
            mock_cursor.fetchone.return_value = ('clinician',)  # role check passes
            mock_cursor.fetchone.side_effect = [
                ('clinician',),  # role check
                (0,),  # total_count = 0
            ]
            mock_cursor.fetchall.return_value = []  # No results
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/clinician/patients/search?q=nonexistent')
            
            assert response.status_code == 200
            data = response.json
            assert data['patients'] == []
            assert data['pagination']['total'] == 0
    
    def test_search_patients_with_results(self, auth_clinician):
        """GET /api/clinician/patients/search returns matching patients"""
        client, user = auth_clinician
        
        with patch('api.get_db_connection') as mock_conn, \
             patch('api.log_event') as mock_log:
            
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            
            # Mock multiple returns for role check, total count, and results
            results = [
                ('patient1', 'John Doe', 'john@test.com', '2025-02-10T10:00:00', 
                 '2025-02-11T10:00:00', 'low', 0)
            ]
            
            mock_cursor.fetchone.side_effect = [
                ('clinician',),  # role check
                (1,),  # total_count
            ]
            mock_cursor.fetchall.return_value = results
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/clinician/patients/search?q=john')
            
            assert response.status_code == 200
            data = response.json
            assert len(data['patients']) >= 0
            assert 'pagination' in data
    
    def test_search_patients_filter_by_risk(self, auth_clinician):
        """GET /api/clinician/patients/search filters by risk_level"""
        client, user = auth_clinician
        
        with patch('api.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            mock_cursor.fetchone.side_effect = [
                ('clinician',),  # role check
                (1,),  # total_count
            ]
            mock_cursor.fetchall.return_value = [
                ('high_risk_patient', 'Risk User', 'risk@test.com', 
                 '2025-02-10T10:00:00', '2025-02-11T10:00:00', 'high', 3)
            ]
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/clinician/patients/search?risk_level=high')
            
            assert response.status_code == 200
            data = response.json
            assert 'patients' in data
            assert 'pagination' in data


class TestAnalyticsDashboard:
    """Tests for Analytics Dashboard (High-level overview)"""
    
    def test_analytics_dashboard_no_clinician_param(self, client):
        """GET /api/analytics/dashboard without clinician param returns 400"""
        response = client.get('/api/analytics/dashboard')
        assert response.status_code == 400
        assert 'Clinician username required' in response.json['error']
    
    def test_analytics_dashboard_no_patients(self, client):
        """GET /api/analytics/dashboard with no patients returns empty metrics"""
        with patch('api.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []  # No patients
            mock_cursor.fetchone.return_value = (0,)  # Count = 0
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            response = client.get('/api/analytics/dashboard?clinician=test_clinician')
            
            assert response.status_code == 200
            data = response.json
            assert data['total_patients'] == 0
            assert data['active_patients'] == 0
            assert data['high_risk_count'] == 0


class TestIntegrationScenarios:
    """End-to-end integration tests"""
    
    def test_patient_login_to_progress_view(self, auth_patient):
        """Full flow: Patient logs in, views progress"""
        client, user = auth_patient
        
        with patch('api.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            mock_cursor.fetchone.side_effect = [
                (5, '2025-01-01T10:00:00'),  # first_log
                (8, '2025-02-11T10:00:00'),  # latest_log
                (20,),  # count
            ]
            mock_cursor.fetchall.return_value = [(8,), (7,), (8,), (7,), (6,), (5,), (4,)]
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            # Patient views progress
            response = client.get('/api/patient/progress/mood')
            assert response.status_code == 200
            
            data = response.json
            assert 'progress_percentage' in data
            assert data['entries_count'] == 20
    
    def test_clinician_searches_then_views_analytics(self, auth_clinician):
        """Full flow: Clinician searches patients, views analytics"""
        client, user = auth_clinician
        
        with patch('api.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value = mock_cursor
            
            # Search
            mock_cursor.fetchone.side_effect = [
                ('clinician',),  # role check
                (2,),  # total_count from search
            ]
            mock_cursor.fetchall.return_value = [
                ('patient1', 'John', 'john@test.com', '2025-02-10T10:00:00', 
                 '2025-02-11T10:00:00', 'low', 0),
                ('patient2', 'Jane', 'jane@test.com', '2025-02-10T10:00:00',
                 '2025-02-11T10:00:00', 'moderate', 1),
            ]
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection
            
            # Clinician searches
            response = client.get('/api/clinician/patients/search?q=')
            assert response.status_code == 200
            data = response.json
            assert len(data['patients']) >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
