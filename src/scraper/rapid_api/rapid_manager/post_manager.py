import http.client
import json
import re
from settings.rapid_api_management import rapid_api_management
from database.main import services
class LinkedinPostFetcher:
    def __init__(self, rapidapi_key, rapidapi_host=rapid_api_management.BASE_URL):
        self.rapidapi_key = rapidapi_key
        self.rapidapi_host = rapidapi_host

    def extract_urn(self, post_url):
        """Extracts the URN from the LinkedIn post URL."""
        match = re.search(r"urn:li:activity:(\d+)", post_url)
        return match.group(1) if match else None

    def get_comments(self, urn):
        """Fetches comments for a given LinkedIn post URN."""
        if not urn:
            return []

        conn = http.client.HTTPSConnection(self.rapidapi_host)
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host
        }

        endpoint = f"/get-profile-post-and-comments?urn={urn}"
        conn.request("GET", endpoint, headers=headers)

        res = conn.getresponse()
        data = res.read()

        try:
            json_data = json.loads(data.decode("utf-8"))
            comments_list = json_data.get('data', {}).get('comments', [])

            if not isinstance(comments_list, list):
                return []

            formatted_comments = [
                {
                    "name": f"{comment.get('author', {}).get('firstName', '')} {comment.get('author', {}).get('lastName', '')}".strip(),
                    "linkedinUrl": comment.get("author", {}).get("linkedinUrl", ""),
                    "title": comment.get("author", {}).get("title", ""),
                    "text": comment.get("text", "")
                }
                for comment in comments_list
            ]

            return formatted_comments
        except json.JSONDecodeError:
            return []

    def get_reactions(self, post_url):
        """Fetches reactions for a given LinkedIn post URL."""
        if not post_url:
            return []

        conn = http.client.HTTPSConnection(self.rapidapi_host)
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host,
            'Content-Type': "application/json"
        }

        payload = json.dumps({"url": post_url, "page": 1})
        conn.request("POST", "/get-post-reactions", payload, headers)

        res = conn.getresponse()
        data = res.read()

        try:
            json_data = json.loads(data.decode("utf-8"))
            reactions_list = json_data.get("data", {}).get('items', [])

            if not isinstance(reactions_list, list):
                return []

            formatted_reactions = [
                {
                    "fullName": reaction.get("fullName", ""),
                    "headline": reaction.get("headline", ""),
                    "reactionType": reaction.get("reactionType", ""),
                    "profileUrl": reaction.get("profileUrl", "")
                }
                for reaction in reactions_list
            ]

            return formatted_reactions
        except json.JSONDecodeError:
            return []


    
    def get_profile_posts(self, username, post_reactions="no", post_comments="no", upper_limit=0, lower_limit=0):
        """Fetches posts for a given LinkedIn username with optional reactions/comments and slicing."""

        if not username:
            return {"error": "Username is required"}

        conn = http.client.HTTPSConnection(self.rapidapi_host)
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host
        }

        endpoint = f"/get-profile-posts?username={username}&limit={upper_limit-lower_limit}"
        conn.request("GET", endpoint, headers=headers)

        res = conn.getresponse()
        data = res.read()

        try:
            json_data = json.loads(data.decode("utf-8"))
            posts = json_data.get("data", [])

            # Adjust upper_limit if not explicitly set
            if upper_limit == 0 or upper_limit > len(posts):
                upper_limit = len(posts)

            # Ensure limits are within range
            lower_limit = max(0, lower_limit)
            upper_limit = max(lower_limit, upper_limit)

            filtered_data = []
            for post in posts[lower_limit:upper_limit]:
                if isinstance(post, dict):
                    post_url = post.get("postUrl")
                    share_url = post.get("shareUrl")

                    urn = self.extract_urn(post_url)
                    comments = self.get_comments(urn) if post_comments == "yes" and urn else []
                    reactions = self.get_reactions(share_url) if post_reactions == "yes" and share_url else []
                    temporary_data={
                        "text": post.get("text"),
                        "shareUrl": share_url,
                        "postUrl": post_url,
                        "totalreactions":post.get("totalReactionCount"),
                        "totalcomments":post.get("commentsCount"),
                        "media": post.get("image"),
                        "comments": comments,
                        "reactions": reactions[:10]
                    }
                    services['activity_posts_service'].save_post_with_details(temporary_data,username)
                    filtered_data.append(temporary_data)

            return filtered_data

        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from API"}
