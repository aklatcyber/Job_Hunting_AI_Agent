import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
import json


load_dotenv()

# Scrape job information from google

def scrape_job_profile(name: str):

    api_key = os.environ["SERP_API_KEY"]
    
    params = {
        "engine": "google_jobs",
        "q": name,
        "gl": "ca",
        "location": "canada",
        "hl": "en",
        "google_domain": "google.ca",
        "ltype": True,
        "api_key": api_key,
        
        }
  
    search = GoogleSearch(params)
    # Get results from the current search page
    results = search.get_dict()
    jobs_result_lookup = results['jobs_results']

    # Filter the accumulated data
    filtered_data = [
        {k: v for k, v in item.items()
         if v not in ([], "", None) and k not in ["share_link", "thumbnail", "job_id","detected_extensions","description"]}
        for item in jobs_result_lookup 
    ]

    # Convert the filtered data to JSON format
    jobs_result_lookup = json.dumps(filtered_data, indent=4)
    
    # Return the JSON data
    return jobs_result_lookup

# Call the function and get the JSON data
# filtered_json_data = scrape_job_profile(name="Senior Software Engineer")
# print(filtered_json_data)
