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
    all_results = []
    search = GoogleSearch(params)
    
    while True:
        # Get results from the current search page
        results = search.get_dict()
        
        # Collect the job results
        jobs_result_lookup = results.get('jobs_results', [])
        all_results.extend(jobs_result_lookup)

        if 'error' in results:
            print(f"Error: {results['error']}")
            break
        
        # Handle pagination
        pagination = results.get("serpapi_pagination", {})
        next_page_token = pagination.get("next_page_token")
        
        if next_page_token:
            params['next_page_token'] = next_page_token
            search = GoogleSearch(params)
        else:
            break


    # Filter the accumulated data
    filtered_data = [
        {k: v for k, v in item.items()
         if v not in ([], "", None) and k not in ["share_link", "thumbnail", "job_id","detected_extensions","description","job_highlights"]}
        for item in all_results
    ]

    # Convert the filtered data to JSON format
    json_data = json.dumps(filtered_data, indent=4)
    
    # Return the JSON data
    return json_data

# Call the function and get the JSON data
# filtered_json_data = scrape_job_profile(name="Senior Software Engineer")
# print(json.dumps(filtered_json_data, indent=4))
# print(filtered_json_data)