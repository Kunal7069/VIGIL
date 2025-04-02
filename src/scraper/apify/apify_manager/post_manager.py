from apify_client import ApifyClient
import json
import re
from settings.apify_management import apify_management
class ApifyScraper:
    def __init__(self, api_token,actor_token):
        # Initialize the Apify client with the provided API token
        self.actor_token= actor_token
        self.client = ApifyClient(api_token)

    def extract_username(self, linkedin_url):
        """Extract the LinkedIn username from the URL"""
        match = re.search(r"linkedin.com/in/([a-zA-Z0-9-]+)/?", linkedin_url)
        return match.group(1) if match else "default_filename"

    def scrape_profiles(self, profiles_url, cookies):
        try:
            """Scrape profiles using Apify API"""
            results = []
            count = 1
            
            print(f"Processing profile {count}: {profiles_url}")
            count += 1
            
            # Extract username from URL
            username = self.extract_username(profiles_url[0])
            
            # Prepare the Actor input
            run_input = {
                "urls": profiles_url,
                "deepScrape": True,
                "rawData": False,
                "minDelay": apify_management.MINIMUM_DEPLY,
                "maxDelay": apify_management.MAXIMUM_DELAY,
                "limitPerSource": apify_management.NUMBER_OF_POSTS,
                "cookie": cookies , # Use the user-provided cookies
                "proxy": {
                    "useApifyProxy": True,
                    "apifyProxyCountry": "US"
                },
                    }
            
            # Trigger the Apify actor with the input
            run = self.client.actor(self.actor_token).call(run_input=run_input)
            
            # Append the results for each profile (this can be saved or processed further)
            results = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            return results
        except Exception as e:
            print(e)
