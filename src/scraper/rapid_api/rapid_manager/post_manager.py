import http.client
import json
import re
from settings.rapid_api_management import rapid_api_management
from database.main import services
import time
class LinkedinPostFetcher:
    def __init__(self, rapidapi_key, rapidapi_host=rapid_api_management.BASE_URL):
        self.rapidapi_key = rapidapi_key
        self.rapidapi_host = rapidapi_host

    def extract_urn(self, post_url):
        """Extracts the URN from the LinkedIn post URL."""
        match = re.search(r"urn:li:activity:(\d+)", post_url)
        return match.group(1) if match else None

    def get_comments(self, urn,comment_limit):
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

            return formatted_comments[:comment_limit]
        except json.JSONDecodeError:
            return []

    
    
    def get_reactions(self, post_url, reaction_limit):
        """Fetches up to `reaction_limit` reactions for a given LinkedIn post URL."""
        if not post_url:
            return []

        all_reactions = []
        page = 1

        while len(all_reactions) < reaction_limit:
            conn = http.client.HTTPSConnection(self.rapidapi_host)
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': self.rapidapi_host,
                'Content-Type': "application/json"
            }

            payload = json.dumps({"url": post_url, "page": page})
            conn.request("POST", "/get-post-reactions", payload, headers)

            res = conn.getresponse()
            data = res.read()

            try:
                json_data = json.loads(data.decode("utf-8"))
                reactions_list = json_data.get("data", {}).get('items', [])

                if not reactions_list:
                    break  # Stop if no more reactions are available

                formatted_batch = [
                    {
                        "fullName": reaction.get("fullName", ""),
                        "headline": reaction.get("headline", ""),
                        "reactionType": reaction.get("reactionType", ""),
                        "profileUrl": reaction.get("profileUrl", "")
                    }
                    for reaction in reactions_list
                ]

                all_reactions.extend(formatted_batch)

                if len(all_reactions) >= reaction_limit:
                    break  # Stop when enough reactions are collected

                page += 1  # Move to the next page
                time.sleep(1.5)  # Optional: Respect rate limits

            except json.JSONDecodeError:
                break  # Exit on JSON parsing error

        return all_reactions[:reaction_limit]

 
    
    def get_profile_posts(self, username, post_reactions="no", post_comments="no", post_limit=0,comment_limit=0,reaction_limit=0):
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
            endpoint = f"/get-profile-posts?username={username}&start={start}"
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
                    share_url = post.get("shareUrl")

                    urn = self.extract_urn(post_url)
                    
                    comments = self.get_comments(urn,comment_limit) if post_comments == "yes" and urn else []
                    reactions = self.get_reactions(share_url,reaction_limit) if post_reactions == "yes" and post_url else []
    
                    temporary_data={
                        "text": post.get("text"),
                        "shareUrl": share_url,
                        "postUrl": post_url,
                        "totalreactions":post.get("totalReactionCount"),
                        "totalcomments":post.get("commentsCount"),
                        "media": post.get("image") if post.get("image") else post.get("resharedPost", {}).get("image"),
                        "original_post_text": post.get("resharedPost", {}).get("text","No original post text available"),
                        "comments": comments[:post_limit],
                        "reactions": reactions[:10],
                        "video":post.get("video") if post.get("video") else []
                    }
                    services['activity_posts_service'].save_post_with_details(temporary_data,username)
                    filtered_data.append(temporary_data)

            return filtered_data

        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from API"}