import pandas as pd
import json
import time
import requests
from requests.exceptions import RequestException
import re
from dotenv import load_dotenv
import os

# Global variables
YOUTRACK_URL = None
AUTH_TOKEN = None
PROJECT_ID = None
BATCH_SIZE = None
BATCH_DELAY = None
MAX_RETRIES = None
INITIAL_RETRY_DELAY = None
CSV_FILE_PATH = None

def load_environment_variables():
    """Load and assign environment variables from .env file.
    
    This function should be called before any other functions that use these variables.
    """
    global YOUTRACK_URL, AUTH_TOKEN, PROJECT_ID, BATCH_SIZE, BATCH_DELAY
    global MAX_RETRIES, INITIAL_RETRY_DELAY, CSV_FILE_PATH
    
    YOUTRACK_URL = os.getenv("YOUTRACK_URL")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    PROJECT_ID = os.getenv("PROJECT_ID")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
    BATCH_DELAY = int(os.getenv("BATCH_DELAY", "3"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    INITIAL_RETRY_DELAY = int(os.getenv("INITIAL_RETRY_DELAY", "3"))
    CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

def load_issues_from_csv():
    """Load issues from CSV file and convert them to the required format.
    
    Returns:
        list: A list of dictionaries containing the formatted issues
    """
    df = pd.read_csv(CSV_FILE_PATH)
    
    issues = []
    for _, row in df.iterrows():
        # Sanitize both summary and description
        sanitized_summary = sanitize_text(row["summary"])
        sanitized_description = sanitize_text(row["description"])
        
        issue = {
            "project": { "id": PROJECT_ID },
            "summary": sanitized_summary,
            "description": sanitized_description
        }
        issues.append(issue)
    
    return issues

def sanitize_text(text):
    """Sanitize text to ensure it's JSON-safe and doesn't contain problematic characters.
    
    Args:
        text: The text to sanitize
        
    Returns:
        str: The sanitized text
    """
    if not isinstance(text, str):
        return str(text)
    
    # Replace null bytes
    text = text.replace('\0', '')
    
    # Replace control characters with spaces
    text = ''.join(char if char.isprintable() or char == '\n' else ' ' for char in text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Ensure the text is not too long (YouTrack might have limits)
    max_length = 1000  # Adjust this based on YouTrack's limits
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text.strip()

def create_issues_batch(batch, retry_count=0):
    """Send a batch of issues to YouTrack with retry logic.
    
    Args:
        batch: List of issues to send
        retry_count: Current retry attempt number
        
    Returns:
        bool: True if successful, False otherwise
    """
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(YOUTRACK_URL, headers=headers, data=json.dumps(batch))
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully created {len(batch)} issues.")
            return True
        elif response.status_code == 429:  # Too Many Requests
            if retry_count < MAX_RETRIES:
                delay = INITIAL_RETRY_DELAY * (2 ** retry_count)  # Exponential backoff
                print(f"Rate limit hit. Waiting {delay} seconds before retry {retry_count + 1}/{MAX_RETRIES}...")
                time.sleep(delay)
                return create_issues_batch(batch, retry_count + 1)
            else:
                print(f"Error: Max retries reached for rate limit. Response: {response.text}")
                return False
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
            
    except RequestException as e:
        print(f"Network error: {str(e)}")
        return False

def process_batches(issues):
    """Process issues in batches and send them to YouTrack.
    
    Args:
        issues: List of issues to process
        
    Returns:
        tuple: (successful_batches, failed_batches)
    """
    total_issues = len(issues)
    successful_batches = 0
    failed_batches = 0
    
    print(f"Starting upload of {total_issues} issues in batches of {BATCH_SIZE}")
    
    for i in range(0, total_issues, BATCH_SIZE):
        batch = issues[i:i + BATCH_SIZE]
        print(f"\nProcessing batch {i//BATCH_SIZE + 1} ({len(batch)} issues)...")
        
        if create_issues_batch(batch):
            successful_batches += 1
        else:
            failed_batches += 1
        
        # Only delay if there are more batches to process
        if i + BATCH_SIZE < total_issues:
            print(f"Waiting {BATCH_DELAY} seconds before next batch...")
            time.sleep(BATCH_DELAY)
    
    return successful_batches, failed_batches

def main():
    """Main entry point for the script."""
    # Load environment variables
    load_dotenv()
    load_environment_variables()
    
    # Load issues from CSV
    issues = load_issues_from_csv()
    
    # Process the batches
    successful_batches, failed_batches = process_batches(issues)
    
    print(f"\nUpload complete!")
    print(f"Summary:")
    print(f"   - Total batches: {successful_batches + failed_batches}")
    print(f"   - Successful batches: {successful_batches}")
    print(f"   - Failed batches: {failed_batches}")

if __name__ == "__main__":
    main() 