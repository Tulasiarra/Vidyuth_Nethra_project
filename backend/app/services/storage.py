import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
# Use service role key if available, fallback to publishable key
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
BUCKET_NAME = "vidhyuth-netra-assets"

def upload_file_to_supabase(file_content: bytes, file_name: str, content_type: str) -> str:
    """
    Uploads file content directly to the Supabase Storage bucket via REST API.
    Returns the public URL of the uploaded file.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase storage configuration is missing. Ensure NEXT_PUBLIC_SUPABASE_URL and SUPABASE_KEY are configured.")
    
    # Ensure URL formatting
    base_url = SUPABASE_URL.rstrip('/')
    url = f"{base_url}/storage/v1/object/{BUCKET_NAME}/{file_name}"
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": content_type
    }
    
    # Attempt to upload (POST)
    response = requests.post(url, headers=headers, data=file_content)
    
    if response.status_code == 200:
        return f"{base_url}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
    elif response.status_code in [400, 409]: # Already exists
        # Overwrite using PUT
        response_put = requests.put(url, headers=headers, data=file_content)
        if response_put.status_code == 200:
            return f"{base_url}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
        else:
            raise IOError(f"Failed to overwrite file in Supabase storage: {response_put.text}")
    else:
        raise IOError(f"Failed to upload to Supabase storage: {response.text}")
