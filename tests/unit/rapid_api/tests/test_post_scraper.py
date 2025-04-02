import pytest
import json
from unittest.mock import patch, Mock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.scraper.rapid_api.rapid_manager.post_manager import LinkedinPostFetcher  


@pytest.fixture
def fetcher():
    return LinkedinPostFetcher(rapidapi_key="fake-key")


def test_extract_urn_valid(fetcher):
    url = "https://www.linkedin.com/feed/update/urn:li:activity:1234567890123456789"
    assert fetcher.extract_urn(url) == "1234567890123456789"


def test_extract_urn_invalid(fetcher):
    url = "https://www.linkedin.com/feed/update/something-else"
    assert fetcher.extract_urn(url) is None


@patch("http.client.HTTPSConnection")
def test_get_comments_valid_json(mock_conn_class, fetcher):
    mock_conn = Mock()
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        "data": {
            "comments": [
                {
                    "author": {
                        "firstName": "John",
                        "lastName": "Doe",
                        "linkedinUrl": "http://linkedin.com/in/john",
                        "title": "Engineer"
                    },
                    "text": "Nice post!"
                }
            ]
        }
    }).encode("utf-8")
    mock_conn.getresponse.return_value = mock_response
    mock_conn_class.return_value = mock_conn

    result = fetcher.get_comments("123456")
    assert result == [{
        "name": "John Doe",
        "linkedinUrl": "http://linkedin.com/in/john",
        "title": "Engineer",
        "text": "Nice post!"
    }]


@patch("http.client.HTTPSConnection")
def test_get_comments_malformed_json(mock_conn_class, fetcher):
    mock_conn = Mock()
    mock_response = Mock()
    mock_response.read.return_value = b"not-json"
    mock_conn.getresponse.return_value = mock_response
    mock_conn_class.return_value = mock_conn

    result = fetcher.get_comments("123456")
    assert result == []


def test_get_comments_empty_urn(fetcher):
    assert fetcher.get_comments(None) == []


@patch("http.client.HTTPSConnection")
def test_get_reactions_valid_json(mock_conn_class, fetcher):
    mock_conn = Mock()
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        "data": {
            "items": [
                {
                    "fullName": "Jane Smith",
                    "headline": "CEO",
                    "reactionType": "LIKE",
                    "profileUrl": "http://linkedin.com/in/jane"
                }
            ]
        }
    }).encode("utf-8")
    mock_conn.getresponse.return_value = mock_response
    mock_conn_class.return_value = mock_conn

    result = fetcher.get_reactions("https://linkedin.com/post")
    assert result == [{
        "fullName": "Jane Smith",
        "headline": "CEO",
        "reactionType": "LIKE",
        "profileUrl": "http://linkedin.com/in/jane"
    }]


@patch("http.client.HTTPSConnection")
def test_get_reactions_malformed_json(mock_conn_class, fetcher):
    mock_conn = Mock()
    mock_response = Mock()
    mock_response.read.return_value = b"bad-json"
    mock_conn.getresponse.return_value = mock_response
    mock_conn_class.return_value = mock_conn

    result = fetcher.get_reactions("someurl")
    assert result == []


def test_get_reactions_no_url(fetcher):
    assert fetcher.get_reactions(None) == []



@patch("http.client.HTTPSConnection")
def test_get_profile_posts_malformed_json(mock_conn_class, fetcher):
    mock_conn = Mock()
    mock_response = Mock()
    mock_response.read.return_value = b"bad-json"
    mock_conn.getresponse.return_value = mock_response
    mock_conn_class.return_value = mock_conn

    result = fetcher.get_profile_posts("someuser")
    assert result == {"error": "Invalid JSON response from API"}


def test_get_profile_posts_empty_username(fetcher):
    result = fetcher.get_profile_posts("")
    assert result == {"error": "Username is required"}
