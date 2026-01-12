"""
Supabase Client - Database Operations
======================================
Provides functions to interact with the Supabase database:
- insert_row: Saves a new note to the reading_notes table
- list_topics: Returns all unique topics in the vault
"""

import os
import sys
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# Database connection settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def get_client():
    """
    Initializes and returns the Supabase client.
    Exits with error if credentials are missing.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        error_msg = {"success": False, "error": "Missing Supabase credentials in .env"}
        print(json.dumps(error_msg), file=sys.stderr)
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_row(content, topic="General Research", insight_tag="Raw Note"):
    """
    Inserts a raw snippet into the reading_notes table.
    
    Args:
        content: The raw text to save
        topic: Category/topic for the note (default: "General Research")
        insight_tag: Short label for the note (default: "Raw Note")
    """
    try:
        supabase = get_client()
        
        # Prepare data payload
        data = {
            "content": content,
            "topic": topic.strip(),
            "insight_tag": insight_tag.strip()
        }
        
        # Insert into database
        result = supabase.table("reading_notes").insert(data).execute()
        
        # Output success for Claude to parse
        print(json.dumps({"success": True, "data": result.data}))
        
    except Exception as e:
        # Output error to stderr for debugging
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


def list_topics():
    """
    Fetches all unique topics from the vault.
    Returns a sorted list of topic names.
    """
    try:
        supabase = get_client()
        
        # Fetch only the 'topic' column to minimize data transfer
        result = supabase.table("reading_notes").select("topic").execute()
        
        if not result.data:
            return []
        
        # Extract unique topics and sort alphabetically
        unique_topics = sorted(list(set([row['topic'] for row in result.data])))
        return unique_topics
        
    except Exception as e:
        # Log error but return empty list (non-critical for UI)
        print(f"Error fetching topics: {e}", file=sys.stderr)
        return []


# --- CLI Entry Point ---
# This script can be called directly from the command line by Claude
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        # Mode: List all topics
        topics = list_topics()
        print(json.dumps(topics))
    elif len(sys.argv) >= 3:
        # Mode: Insert a new note
        # Usage: python supabase_client.py "content" "topic"
        content = sys.argv[1]
        topic = sys.argv[2]
        insert_row(content=content, topic=topic)
    else:
        # Show usage help
        print("Usage: python supabase_client.py <content> <topic> OR python supabase_client.py --list", file=sys.stderr)
        sys.exit(1)