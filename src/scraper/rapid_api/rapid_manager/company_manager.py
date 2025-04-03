import http.client
import json
import re
from settings.rapid_api_management import rapid_api_management
from database.main import services
from scraper.rapid_api.rapid_manager.post_manager import LinkedinPostFetcher
import os 
from dotenv import load_dotenv

load_dotenv()

RAPID_API_KEY = os.getenv("RAPID_API_KEY")
linkedin_post_fetcher = LinkedinPostFetcher(RAPID_API_KEY)

class CompanyPostFetcher:
    def __init__(self, rapidapi_key, rapidapi_host=rapid_api_management.BASE_URL):
        self.rapidapi_key = rapidapi_key
        self.rapidapi_host = rapidapi_host

    def extract_urn(self, post_url):
        """Extracts the URN from the LinkedIn post URL."""
        match = re.search(r"urn:li:activity:(\d+)", post_url)
        return match.group(1) if match else None

   
    def get_company_posts(self, username, post_reactions="no", post_comments="no", upper_limit=0, lower_limit=0):
        """Fetches posts for a given LinkedIn username with optional reactions/comments and slicing."""

        if not username:
            return {"error": "Username is required"}

        conn = http.client.HTTPSConnection(self.rapidapi_host)
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host
        }

        endpoint = f"/get-company-posts?username={username}&start=0"
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
            print("LEN",len(posts))
            for post in posts[lower_limit:upper_limit]:
                if isinstance(post, dict):
                    post_url = post.get("postUrl")
                    share_url = post.get("shareUrl", "none")
    
                    urn = self.extract_urn(post_url)
        
                    comments = linkedin_post_fetcher.get_comments(urn) if post_comments == "yes" and urn else []
                  
                    # reactions = linkedin_post_fetcher.get_reactions(share_url) if post_reactions == "yes" and share_url else []
                    reactions = linkedin_post_fetcher.get_reactions(post_url) if post_reactions == "yes" and post_url else []
                   
                    temporary_data={
                        "text": post.get("text"),
                        "shareUrl": share_url,
                        "postUrl": post_url,
                        "totalreactions":post.get("totalReactionCount"),
                        "totalcomments":post.get("commentsCount"),
                        "media": post.get("image") if post.get("image") else post.get("resharedPost", {}).get("image"),
                        "original_post_text": post.get("resharedPost", {}).get("text","No original post text available"),
                        "comments": comments,
                        "reactions": reactions[:10],
                        "video":post.get("video") if post.get("video") else []
                    }
                   
                    services['activity_posts_service'].save_post_with_details(temporary_data,username)
                    filtered_data.append(temporary_data)

            return filtered_data

        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from API"}
