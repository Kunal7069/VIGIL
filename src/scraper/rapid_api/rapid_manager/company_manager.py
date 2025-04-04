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

    def fetch_share_url(self,post_url):
        """Fetches shareUrl from LinkedIn post API if not available."""
        conn = http.client.HTTPSConnection(self.rapidapi_host)
        
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host
        }
        
        endpoint = f"/get-post?url={post_url}"
        conn.request("GET", endpoint, headers=headers)
        
        res = conn.getresponse()
        data = res.read()

        try:
            json_data = json.loads(data.decode("utf-8"))
            return json_data.get("data", {}).get("shareUrl", "none")
        except json.JSONDecodeError:
            return "none"
    
    def get_company_posts(self, username, post_reactions="no", post_comments="no", post_limit=0,comment_limit=0,reaction_limit=0):
        """Fetches posts for a given LinkedIn username with optional reactions/comments and slicing."""

        if not username:
            return {"error": "Username is required"}

        conn = http.client.HTTPSConnection(self.rapidapi_host)
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.rapidapi_host
        }

        all_posts = []
        start = 0
        pagination_token = None

        while len(all_posts) < post_limit:
            endpoint = f"/get-company-posts?username={username}&start={start}"
            if pagination_token:
                endpoint += f"&paginationToken={pagination_token}"
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()

            try:
                json_data = json.loads(data.decode("utf-8"))
                posts = json_data.get("data", [])
                all_posts.extend(posts)

                # If post_limit is reached, break
                if len(all_posts) >= post_limit:
                    break

                # Update pagination token for next request
                pagination_token = json_data.get("paginationToken")
                if not pagination_token:
                    break  # No more pages available

                start += 50  # Move to the next batch
            
            except json.JSONDecodeError:
                return {"error": "Failed to parse response"}

        try:
           
            posts = all_posts[:post_limit]
            filtered_data = []
           
            for post in posts:
                if isinstance(post, dict):
                    post_url = post.get("postUrl")
                    share_url = post.get("shareUrl", "none")
                   
                    if share_url == "none" and post_url:
                        share_url = self.fetch_share_url(post_url)
                    
                    urn = self.extract_urn(post_url)
            
                    comments = linkedin_post_fetcher.get_comments(urn,comment_limit) if post_comments == "yes" and urn else []
                    
                    reactions = linkedin_post_fetcher.get_reactions(share_url,reaction_limit) if post_reactions == "yes" and post_url else []
                    
                    temporary_data={
                        "text": post.get("text"),
                        "shareUrl": share_url,
                        "postUrl": post_url,
                        "totalreactions":post.get("totalReactionCount"),
                        "totalcomments":post.get("commentsCount"),
                        "media": post.get("image") if post.get("image") else post.get("resharedPost", {}).get("image"),
                        "original_post_text": post.get("resharedPost", {}).get("text","No original post text available"),
                        "comments": comments,
                        "reactions": reactions,
                        "video":post.get("video") if post.get("video") else []
                    }
                   
                    services['activity_posts_service'].save_post_with_details(temporary_data,username)
                    filtered_data.append(temporary_data)

            return filtered_data

        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from API"}

    