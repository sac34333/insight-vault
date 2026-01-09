"""
InsightVault - Main Agent Orchestrator
======================================
This script initializes the Claude SDK client and manages:
1. Clipboard monitoring (background task)
2. User command processing (foreground task)
"""

import os
import asyncio
import pyperclip
import sys
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock

# --- PATH CONFIGURATION ---
# Add the skill folder to Python's path so we can import helper functions
skill_path = os.path.join(".claude", "skills", "capture-insight")
if skill_path not in sys.path:
    sys.path.append(skill_path)

# Import the list_topics helper (used for /list command)
try:
    from supabase_client import list_topics
except ImportError:
    # Fallback if the supabase_client module is not found
    def list_topics(): return []

# Load environment variables from .env file
load_dotenv()

# --- GLOBAL STATE ---
current_topic = "General Research"  # Default topic for new captures
seen_messages = set()               # Tracks printed messages to avoid duplicates


def print_menu():
    """Displays the current topic and available commands to the user."""
    global current_topic
    print("\n" + "="*50)
    print(f"STATUS: LOCKED TOPIC -> {current_topic}")
    print("-" * 50)
    print("-> [Auto-Capture] Press Ctrl+C on any text to save.")
    print("-> [/topic <name>] or [/ <name>] Change research topic.")
    print("-> [/list]         See all existing topics in your vault.")
    print("-> [I am done]     Publish current topic to Confluence.")
    print("="*50 + "\n")


async def handle_agent_responses(client):
    """
    Processes and displays Claude's responses.
    - Filters duplicate "Vault Updated" messages
    - Highlights Confluence URLs with success formatting
    """
    global seen_messages
    
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                # Log tool executions for transparency
                if isinstance(block, ToolUseBlock):
                    print(f"[System]: Executing {block.name}...")
                
                elif isinstance(block, TextBlock):
                    text = block.text.strip()
                    if not text:
                        continue

                    # Prevent duplicate "Vault Updated" messages
                    if "Vault Updated" in text:
                        if text not in seen_messages:
                            print(f"Agent: {text}")
                            seen_messages.add(text)
                    # Highlight Confluence publish success
                    elif "http" in text or "Published" in text or "atlassian.net" in text:
                        print(f"\n🚀 SUCCESS: {text}")
                    else:
                        print(f"Agent: {text}")
    
    # Clear seen messages for the next interaction cycle
    seen_messages.clear()
    print_menu()


async def clipboard_listener(client):
    """
    Background task: Monitors clipboard for new content.
    When new text is detected, sends it to Claude with the current topic.
    """
    global current_topic
    
    # Store initial clipboard content to detect changes
    last_clip = pyperclip.paste().strip()
    
    while True:
        try:
            current_clip = pyperclip.paste().strip()
            
            # Only process if clipboard has new content
            if current_clip and current_clip != last_clip:
                last_clip = current_clip
                # Show preview (first 60 chars)
                print(f"\n[Raw Capture]: {current_clip[:60]}...")
                
                # Send to Claude with topic context (Topic Lock pattern)
                query_text = f"TOPIC: {current_topic} | Raw capture: '{current_clip}'. Save as-is."
                await client.query(query_text)
                asyncio.create_task(handle_agent_responses(client))
            
            # Poll every 500ms
            await asyncio.sleep(0.5)
        except Exception:
            # On error, wait a bit longer before retrying
            await asyncio.sleep(1)


async def user_input_loop(client):
    """
    Foreground task: Handles user commands from the terminal.
    Supports: /list, /topic, I am done, and general queries.
    """
    global current_topic
    
    while True:
        try:
            # Read user input in a non-blocking way
            user_text = await asyncio.to_thread(input, "You: ")
            
            # Skip empty input
            if not user_text.strip():
                continue

            # --- COMMAND: List all topics ---
            if user_text.strip() == "/list":
                topics = list_topics()
                if topics:
                    print("\n--- Topics found in your Vault ---")
                    for t in topics:
                        print(f" • {t}")
                    print("----------------------------------")
                else:
                    print("\n[System]: No topics found in vault yet.")
                print_menu()
                continue

            # --- COMMAND: Switch topic ---
            # Supports: /topic <name>, / <name>, or /<name>
            if user_text.startswith("/topic ") or user_text.startswith("/ ") or user_text.startswith("/"):
                # Handle edge case: "/list" should not trigger topic switch
                if user_text.strip() == "/list":
                    continue
                    
                # Extract topic name by removing command prefixes
                new_topic = user_text.replace("/topic ", "").replace("/ ", "")
                if new_topic.startswith("/"):
                    new_topic = new_topic[1:]
                
                # Avoid setting empty topic
                if new_topic.strip():
                    current_topic = new_topic.strip()
                    print(f"\n[System]: Topic updated and locked to: {current_topic}")
                else:
                    print("\n[System]: Please provide a topic name.")
                print_menu()
                continue

            # --- COMMAND: Publish to Confluence ---
            if "I am done" in user_text or "Publish" in user_text:
                publish_query = f"I am done. Publish all research notes for the topic '{current_topic}' to Confluence."
                await client.query(publish_query)
            else:
                # Pass any other text as a general query to Claude
                await client.query(user_text)
            
            await handle_agent_responses(client)

        except Exception as e:
            print(f"Input Error: {e}")


async def main():
    """
    Entry point: Initializes the Claude SDK client and starts both tasks.
    """
    # Load CLI path from environment (supports Windows/Mac/Linux)
    env_cli_path = os.getenv("CLAUDE_CLI_PATH", "claude")
    
    # Configure the Claude Agent SDK
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        cli_path=env_cli_path,
        cwd="./",
        setting_sources=["project"],
        allowed_tools=["Skill", "Bash", "Read", "Write"]
    )

    print("\n(venv) InsightVault: Power Research Mode Active.")
    print_menu()

    # Start the async client and run both tasks concurrently
    async with ClaudeSDKClient(options=options) as client:
        await asyncio.gather(
            clipboard_listener(client),  # Background: monitors clipboard
            user_input_loop(client)       # Foreground: handles commands
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession ended. Your insights are safe in the vault.")