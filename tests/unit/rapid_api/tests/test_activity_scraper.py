import pytest
import json
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
# Import the class to test
from src.settings.rapid_api_management import rapid_api_management
from src.database.main import services
from src.scraper.rapid_api.rapid_manager.activity_manager import LinkedInActivityFetcher

@pytest.fixture
def api_key():
    return "test_api_key"

@pytest.fixture
def test_username():
    return "johndoe"

@pytest.fixture
def mock_profile_data():
    return {
        "username": "johndoe",
        "firstName": "John",
        "lastName": "Doe",
        "profilePicture": "https://example.com/profile.jpg",
        "geo": {"country": "US", "city": "San Francisco"},
        "headline": "Software Engineer",
        "educations": [
            {
                "schoolName": "Stanford University",
                "degree": "BS",
                "fieldOfStudy": "Computer Science",
                "start": {"year": 2015},
                "end": {"year": 2019},
                "description": "Computer Science major",
                "activities": "Coding club",
                "grade": "3.8",
                "url": "https://linkedin.com/school/stanford",
                "schoolId": "123456"
            }
        ],
        "position": [
            {
                "companyId": "789",
                "companyName": "Tech Corp",
                "companyUsername": "techcorp",
                "companyURL": "https://linkedin.com/company/techcorp",
                "companyIndustry": "Technology",
                "companyStaffCountRange": "501-1000",
                "title": "Software Engineer",
                "location": "San Francisco, CA",
                "employmentType": "Full-time",
                "description": "Developing software solutions",
                "start": {"year": 2019, "month": 6},
                "end": {}
            }
        ],
        "fullPositions": [
            {
                "companyId": "789",
                "companyName": "Tech Corp",
                "companyUsername": "techcorp",
                "companyURL": "https://linkedin.com/company/techcorp",
                "companyIndustry": "Technology",
                "companyStaffCountRange": "501-1000",
                "title": "Software Engineer",
                "location": "San Francisco, CA",
                "employmentType": "Full-time",
                "description": "Developing software solutions",
                "start": {"year": 2019, "month": 6},
                "end": {}
            }
        ]
    }

@pytest.fixture
def mock_comments_data():
    return {
        "data": [
            {
                "author": {
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "headline": "Product Manager",
                    "url": "https://linkedin.com/in/janesmith"
                },
                "text": "Great post!",
                "highlightedComments": ["Great post!"],
                "postUrl": "https://linkedin.com/post/123",
                "totalReactionCount": 10,
                "likeCount": 8,
                "appreciationCount": 1,
                "empathyCount": 1,
                "praiseCount": 0,
                "funnyCount": 0,
                "commentsCount": 2,
                "repostsCount": 1
            }
        ]
    }

@pytest.fixture
def mock_likes_data():
    return {
        "data": {
            "items": [
                {
                    "action": "LIKE",
                    "text": "Exciting news about our product launch!",
                    "postUrl": "https://linkedin.com/post/456",
                    "author": {
                        "firstName": "Jane",
                        "lastName": "Smith",
                        "headline": "Product Manager",
                        "url": "https://linkedin.com/in/janesmith"
                    },
                    "totalReactionCount": 25,
                    "likeCount": 20,
                    "empathyCount": 5,
                    "commentsCount": 3
                }
            ]
        }
    }

# Helper context manager for mocking http.client.HTTPSConnection
@contextmanager
def mock_https_connection(response_data, status=200):
    with patch('http.client.HTTPSConnection') as mock_conn:
        mock_response = MagicMock()
        mock_response.status = status
        mock_response.read.return_value = json.dumps(response_data).encode('utf-8')
        mock_conn.return_value.getresponse.return_value = mock_response
        yield mock_conn

# Test the initialization
def test_init(api_key):
    fetcher = LinkedInActivityFetcher(api_key)
    assert fetcher.api_key == api_key
    assert fetcher.base_url == rapid_api_management.BASE_URL
    assert fetcher.headers == {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': rapid_api_management.BASE_URL
    }

# Test _make_request method
def test_make_request(api_key, mock_profile_data):
    fetcher = LinkedInActivityFetcher(api_key)
    endpoint = "/test-endpoint"
    
    with mock_https_connection(mock_profile_data):
        result = fetcher._make_request(endpoint)
        
    assert result == mock_profile_data

# Test _make_request with JSON decode error
def test_make_request_json_error(api_key):
    fetcher = LinkedInActivityFetcher(api_key)
    endpoint = "/test-endpoint"
    
    with patch('http.client.HTTPSConnection') as mock_conn:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = "Invalid JSON".encode('utf-8')
        mock_conn.return_value.getresponse.return_value = mock_response
        
        result = fetcher._make_request(endpoint)
        
    assert result == {"error": "Failed to parse JSON", "response": "Invalid JSON"}

# Test get_profile method
def test_get_profile(api_key, test_username, mock_profile_data):
    fetcher = LinkedInActivityFetcher(api_key)
    
    with mock_https_connection(mock_profile_data):
        result = fetcher.get_profile(test_username)
        
    assert result == mock_profile_data

# Test get_comments method
def test_get_comments(api_key, test_username, mock_comments_data):
    fetcher = LinkedInActivityFetcher(api_key)
    
    with mock_https_connection(mock_comments_data):
        result = fetcher.get_comments(test_username)
        
    assert result == mock_comments_data

# Test get_likes method
def test_get_likes(api_key, test_username, mock_likes_data):
    fetcher = LinkedInActivityFetcher(api_key)
    
    with mock_https_connection(mock_likes_data):
        result = fetcher.get_likes(test_username)
        
    assert result == mock_likes_data
    
    # Test with start parameter
    with mock_https_connection(mock_likes_data):
        result = fetcher.get_likes(test_username, start=10)
        
    assert result == mock_likes_data

# Test extract_comment_details method
def test_extract_comment_details(api_key, test_username, mock_comments_data):
    fetcher = LinkedInActivityFetcher(api_key)
    
    # Create our mocks for the service
    mock_comments_service = MagicMock()
    
    # Store original service to restore it later
    original_service = services.get('activity_comments_service', None)
    
    try:
        # Mock the get_comments method
        with patch.object(fetcher, 'get_comments', return_value=mock_comments_data):
            # Replace the service in the dictionary
            services['activity_comments_service'] = mock_comments_service
            
            # Call the method
            result = fetcher.extract_comment_details(test_username, "test_job_123")
    finally:
        # Restore the original service
        if original_service:
            services['activity_comments_service'] = original_service
        else:
            # If it didn't exist before, remove it
            services.pop('activity_comments_service', None)
            
    # Assert result structure
    assert isinstance(result, list)
    assert len(result) == 1
    comment = result[0]
    assert comment["username"] == test_username
    assert comment["first_name"] == "Jane"
    assert comment["last_name"] == "Smith"
    assert comment["headline"] == "Product Manager"
    assert comment["profile_url"] == "https://linkedin.com/in/janesmith"
    assert comment["post_text"] == "Great post!"
    assert comment["highlighted_comment"] == "Great post!"
    assert comment["post_url"] == "https://linkedin.com/post/123"
    assert comment["total_reactions"] == 10
    assert comment["like_count"] == 8
    
    

# Test extract_comment_details with no data
def test_extract_comment_details_no_data(api_key, test_username):
    fetcher = LinkedInActivityFetcher(api_key)
    
    # Mock the get_comments method to return empty data
    with patch.object(fetcher, 'get_comments', return_value={"data": []}):
        result = fetcher.extract_comment_details(test_username, "test_job_123" )
        
    assert result == {"error": "No comments found"}
    
    # Test with completely invalid response
    with patch.object(fetcher, 'get_comments', return_value={"error": "API error"}):
        result = fetcher.extract_comment_details(test_username ,"test_job_123")
        
    assert result == {"error": "No comments found"}

# Test extract_likes_details method
def test_extract_likes_details(api_key, test_username, mock_likes_data):
    fetcher = LinkedInActivityFetcher(api_key)
    
    # Create our mocks for the service
    mock_reactions_service = MagicMock()
    
    # Store original service to restore it later
    original_service = services.get('activity_reactions_service', None)
    
    try:
        # Mock the get_likes method
        with patch.object(fetcher, 'get_likes', return_value=mock_likes_data):
            # Replace the service in the dictionary
            services['activity_reactions_service'] = mock_reactions_service
            
            # Call the method
            result = fetcher.extract_likes_details(test_username, "test_job_123")
    finally:
        # Restore the original service
        if original_service:
            services['activity_reactions_service'] = original_service
        else:
            # If it didn't exist before, remove it
            services.pop('activity_reactions_service', None)
            
    # Assert result structure
    assert isinstance(result, list)
    assert len(result) == 1
    like = result[0]
    assert like["username"] == test_username
    assert like["action"] == "LIKE"
    assert like["post_text"] == "Exciting news about our product launch!"
    assert like["post_url"] == "https://linkedin.com/post/456"
    assert like["first_name"] == "Jane"
    assert like["last_name"] == "Smith"
    assert like["headline"] == "Product Manager"
    assert like["profile_url"] == "https://linkedin.com/in/janesmith"
    assert like["total_reactions"] == 25
    assert like["like_count"] == 20
    assert like["empathy_count"] == 5
    assert like["comments_count"] == 3
    

# Test extract_likes_details with no data
def test_extract_likes_details_no_data(api_key, test_username):
    fetcher = LinkedInActivityFetcher(api_key)
    
    # Mock the get_likes method to return empty data
    with patch.object(fetcher, 'get_likes', return_value={"data": {"items": []}}):
        result = fetcher.extract_likes_details(test_username ,"test_job_123")
        
    assert result == {"error": "No likes found"}
    
    # Test with completely invalid response
    with patch.object(fetcher, 'get_likes', return_value={"error": "API error"}):
        result = fetcher.extract_likes_details(test_username ,"test_job_123")
        
    assert result == {"error": "No likes found"}

# Test extract_clean_profile method
def test_extract_clean_profile(api_key, test_username, mock_profile_data):
    fetcher = LinkedInActivityFetcher(api_key)
    
    # Create our mocks for the service
    mock_profile_service = MagicMock()
    
    # Store original service to restore it later
    original_service = services.get('activity_profile_service', None)
    
    try:
        with patch.object(fetcher, 'get_profile', return_value=mock_profile_data):
            # Replace the service in the dictionary
            services['activity_profile_service'] = mock_profile_service
            
            # Also patch print to avoid cluttering test output
            with patch('builtins.print'):
                # Call the method
                result = fetcher.extract_clean_profile(test_username, "test_job_123")
    finally:
        # Restore the original service
        if original_service:
            services['activity_profile_service'] = original_service
        else:
            # If it didn't exist before, remove it
            services.pop('activity_profile_service', None)
                
    # Assert the profile was processed correctly
    assert result["username"] == "johndoe"
    assert result["first_name"] == "John"
    assert result["last_name"] == "Doe"
    assert result["profile_picture"] == "https://example.com/profile.jpg"
    
    # Check education was mapped correctly
    assert len(result["educations"]) == 1
    edu = result["educations"][0]
    assert edu["school_name"] == "Stanford University"
    assert edu["degree"] == "BS"
    assert edu["field_of_study"] == "Computer Science"
    
    # Check positions were mapped correctly
    assert len(result["positions"]) == 1
    pos = result["positions"][0]
    assert pos["company_name"] == "Tech Corp"
    assert pos["title"] == "Software Engineer"
    assert pos["employment_type"] == "Full-time"
    
    # Check full positions were mapped correctly
    assert len(result["full_positions"]) == 1
    

# Testing edge cases for extract_clean_profile with incomplete data
def test_extract_clean_profile_incomplete_data(api_key, test_username):
    fetcher = LinkedInActivityFetcher(api_key)
    incomplete_data = {
        "username": "johndoe",
        # Missing many fields
    }
    
    with patch.object(fetcher, 'get_profile', return_value=incomplete_data):
        with patch.dict(services, {'activity_profile_service': MagicMock()}):
            # Also patch print to avoid cluttering test output
            with patch('builtins.print'):
                result = fetcher.extract_clean_profile(test_username, "test_job_123")
                
    # Check that default values are used when fields are missing
    assert result["username"] == "johndoe"
    assert result["first_name"] == ""
    assert result["headline"] == ""
    assert result["educations"] == []
    assert result["positions"] == []