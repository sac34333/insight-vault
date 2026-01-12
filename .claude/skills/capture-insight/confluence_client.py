"""
Confluence Client - Publishing Operations
==========================================
Provides functions to publish research notes to Confluence:
- create_or_update_research_page: Creates or updates a page with captured snippets
"""

import os
import sys
import json
from atlassian import Confluence
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()


def get_confluence_client():
    """
    Initializes and returns the Confluence API client.
    Exits with error if credentials are missing.
    """
    site_name = os.getenv("ATLASSIAN_SITE_NAME")
    username = os.getenv("ATLASSIAN_USER_EMAIL")
    token = os.getenv("ATLASSIAN_API_TOKEN")
    
    # Build the Atlassian Cloud URL
    url = f"https://{site_name}.atlassian.net"
    
    # Validate credentials
    if not all([site_name, username, token]):
        print(json.dumps({"success": False, "error": "Missing Atlassian credentials"}), file=sys.stderr)
        sys.exit(1)
    
    # Note: Confluence API uses 'password' param for API token
    return Confluence(url=url, username=username, password=token)


def create_or_update_research_page(title, snippets_json, space='InsightVau'):
    """
    Creates a new Confluence page or updates an existing one.
    
    Args:
        title: Page title (also used to check for existing pages)
        snippets_json: JSON string containing array of note objects
        space: Confluence space key (default: 'QubitlyVen')
    """
    try:
        confluence = get_confluence_client()
        
        # Parse the JSON snippets
        snippets = json.loads(snippets_json)
        
        # Build the HTML content for the page
        html_body = f"<h1>Research Log: {title}</h1><p>Raw insights captured via InsightVault.</p><hr/>"
        
        for i, note in enumerate(snippets, 1):
            content = note.get('content', '')
            # Using <pre> tag preserves formatting and is ideal for code snippets
            html_body += f"<h3>Entry #{i}</h3><pre style='background: #f4f4f4; padding: 10px; border-radius: 5px;'>{content}</pre><hr/>"

        # Check if a page with this title already exists
        existing_page = confluence.get_page_by_title(space=space, title=title)
        
        if existing_page:
            # Update the existing page
            page_id = existing_page['id']
            result = confluence.update_page(
                page_id=page_id,
                title=title,
                body=html_body,
                representation='storage'  # Confluence storage format
            )
            action = "Updated"
        else:
            # Create a new page
            result = confluence.create_page(
                space=space,
                title=title,
                body=html_body,
                representation='storage'
            )
            action = "Created"

        # Output success with the page URL for Claude to display
        print(json.dumps({
            "success": True, 
            "action": action,
            "page_url": result['_links']['base'] + result['_links']['webui']
        }))
        
    except Exception as e:
        # Output error to stderr for debugging
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


# --- CLI Entry Point ---
# This script is called by Claude to publish notes to Confluence
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python confluence_client.py <title> <snippets_json>", file=sys.stderr)
        sys.exit(1)
    
    # Extract arguments and call the publish function
    create_or_update_research_page(sys.argv[1], sys.argv[2])