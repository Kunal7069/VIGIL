import http.client
import json
from settings.rapid_api_management import rapid_api_management
from database.main import services
import time
class LinkedInActivityFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = rapid_api_management.BASE_URL
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.base_url
        }

    def _make_request(self, endpoint):
        """Helper method to make API requests and return JSON response."""
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("GET", endpoint, headers=self.headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")

        try:
            return json.loads(data)  # Convert response string to JSON
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "response": data}

    # def get_likes(self, username, post_limit):
    #     """Fetch LinkedIn likes data."""
    #     endpoint = f"/get-profile-likes?username={username}&start={start}"
    #     return self._make_request(endpoint)
    
    def _make_request_1(self, endpoint):
        """Helper method to make API requests with rate limiting."""
        time.sleep(5)  # Apply delay before each request
        
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("GET", endpoint, headers=self.headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")

        try:
            return json.loads(data)  # Convert response string to JSON
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "response": data}
    
    def get_likes(self, username, post_limit):
        """Fetch LinkedIn likes data with pagination and rate limiting."""
        all_likes = []
        start = 0
        pagination_token = None

        while len(all_likes) < post_limit:
            endpoint = f"/get-profile-likes?username={username}&start={start}"
            if pagination_token:
                endpoint += f"&paginationToken={pagination_token}"

            response = self._make_request_1(endpoint)
            
            likes = response.get("data", [])
    
            all_likes.extend(likes['items'])

            # Stop if we reach post_limit
            if len(all_likes) >= post_limit:
                break

            # Update pagination token
            pagination_token = likes.get("paginationToken")
            if not pagination_token:
                break  # No more pages available

            start += 100  # Move to the next batch
        
        print("LIKES",len(all_likes[:post_limit]))
        return all_likes[:post_limit]
    
    
    def get_profile(self, username):
        """Fetch full LinkedIn profile details."""
        endpoint = f"/?username={username}"
        return self._make_request(endpoint)
    
    def get_company_profile(self, username):
        """Fetch full LinkedIn profile details."""
        endpoint = f"/get-company-details?username={username}"
        return self._make_request(endpoint)

    def get_comments(self, username):
        """Fetch LinkedIn comments data."""
        endpoint = f"/get-profile-comments?username={username}"
        return self._make_request(endpoint)

    

    
    def extract_comment_details(self, username,post_limit,job_id):
        try:
            """
            Extract key details from comments, inject username,
            transform to DB model format, and save to DB.
            """
            comments = self.get_comments(username)
            
            if "data" in comments and isinstance(comments["data"], list) and len(comments["data"]) > 0:
                processed_comments = []

                for comment in comments["data"]:
                    author = comment.get("author", {})

                    processed_comments.append({
                        "username": username,
                        "first_name": author.get("firstName", ""),
                        "last_name": author.get("lastName", ""),
                        "headline": author.get("headline", ""),
                        "profile_url": author.get("url", ""),
                        "post_text": comment.get("text", ""),
                        "highlighted_comment": comment.get("highlightedComments", [""])[0],
                        "post_url": comment.get("postUrl", ""),
                        "total_reactions": comment.get("totalReactionCount", 0),
                        "like_count": comment.get("likeCount", 0),
                        "appreciation_count": comment.get("appreciationCount", 0),
                        "empathy_count": comment.get("empathyCount", 0),
                        "praise_count": comment.get("praiseCount", 0),
                        "funny_count": comment.get("funnyCount", 0),
                        "comments_count": comment.get("commentsCount", 0),
                        "reposts_count": comment.get("repostsCount", 0),
                    })

                # Save using the service
                
                services['activity_comments_service'].save_batch_activity_comments(processed_comments[:post_limit])

                return processed_comments[:post_limit]
            
            else:
                return {"error": "No comments found"}
        except Exception as e:
            services['activity_job_track'].update_status(job_id, "cancelled")
            services['activity_job_track'].add_remark(job_id, f"Scraping activity comments failed: {str(e)}")
            return {"error": f"Scraping activity comments failed for {username}"}

    
    def extract_likes_details(self, username,post_limit,job_id):
        try:
           
            """
            Extract key details from likes, inject username,
            transform to DB model format, and save to DB.
            """
            likes_data = self.get_likes(username,post_limit)
            
            if (len(likes_data) > 0
            ):
                processed_reacions = []

                for like in likes_data:
                    author = like.get("author", {})

                    processed_reacions.append({
                        "username": username,  # tracked profile
                        "action": like.get("action", ""),
                        "post_text": like.get("text", ""),
                        "post_url": like.get("postUrl", ""),
                        "first_name": author.get("firstName", ""),
                        "last_name": author.get("lastName", ""),
                        "headline": author.get("headline", ""),
                        "profile_url": author.get("url", ""),
                        "total_reactions": like.get("totalReactionCount", 0),
                        "like_count": like.get("likeCount", 0),
                        "empathy_count": like.get("empathyCount", 0),
                        "comments_count": like.get("commentsCount", 0),
                    })

                services['activity_reactions_service'].save_batch_activity_reactions(processed_reacions)

                return processed_reacions

            return {"error": "No likes found"}
        
        except Exception as e:
            services['activity_job_track'].update_status(job_id, "cancelled")
            services['activity_job_track'].add_remark(job_id, f"Scraping activity reactions failed: {str(e)}")
            return {"error": f"Scraping activity reactions failed for {username}"}

    
    def extract_clean_user_profile(self, username,job_id):
        try:
            profile_data = self.get_profile(username)
            # Base fields
            result = {
                "username": profile_data.get("username", username),
                "first_name": profile_data.get("firstName", ""),
                "last_name": profile_data.get("lastName", ""),
                "profile_picture": profile_data.get("profilePicture", ""),
                "geo": profile_data.get("geo", {}),
                "headline": profile_data.get("headline", ""),
                "educations": [],
                "positions": [],
                "full_positions": []
            }

            # Educations (without logo)
            for edu in profile_data.get("educations", []):
                result["educations"].append({
                    "school_name": edu.get("schoolName", ""),
                    "degree": edu.get("degree", ""),
                    "field_of_study": edu.get("fieldOfStudy", ""),
                    "start": edu.get("start", {}),
                    "end": edu.get("end", {}),
                    "description": edu.get("description", ""),
                    "activities": edu.get("activities", ""),
                    "grade": edu.get("grade", ""),
                    "url": edu.get("url", ""),
                    "school_id": edu.get("schoolId", "")
                })

            # Positions (exclude logo and multiLocale fields)
            for pos in profile_data.get("position", []):
                result["positions"].append({
                    "company_id": pos.get("companyId"),
                    "company_name": pos.get("companyName", ""),
                    "company_username": pos.get("companyUsername", ""),
                    "company_url": pos.get("companyURL", ""),
                    "industry": pos.get("companyIndustry", ""),
                    "staff_count": pos.get("companyStaffCountRange", ""),
                    "title": pos.get("title", ""),
                    "location": pos.get("location", ""),
                    "employment_type": pos.get("employmentType", ""),
                    "description": pos.get("description", ""),
                    "start": pos.get("start", {}),
                    "end": pos.get("end", {})
                })

            # FullPositions (same cleanup as above)
            for pos in profile_data.get("fullPositions", []):
                result["full_positions"].append({
                    "company_id": pos.get("companyId"),
                    "company_name": pos.get("companyName", ""),
                    "company_username": pos.get("companyUsername", ""),
                    "company_url": pos.get("companyURL", ""),
                    "industry": pos.get("companyIndustry", ""),
                    "staff_count": pos.get("companyStaffCountRange", ""),
                    "title": pos.get("title", ""),
                    "location": pos.get("location", ""),
                    "employment_type": pos.get("employmentType", ""),
                    "description": pos.get("description", ""),
                    "start": pos.get("start", {}),
                    "end": pos.get("end", {})
                })
            
            services['activity_profile_service'].save_profile_bundle(result)
            return result
        except Exception as e:
            services['activity_job_track'].update_status(job_id, "cancelled")
            services['activity_job_track'].add_remark(job_id, f"Profile scraping failed: {str(e)}")
            return {"error": f"Profile scraping failed for {username}"}

    
    
    def extract_clean_company_profile(self, username,job_id):
        company_profile_data=self.get_company_profile(username)
        return company_profile_data
        