import os
import asyncio
import pyperclip
import sys
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock

# --- PATH CONFIGURATION ---
# Tell Python to look inside the hidden skill folder for your logic
skill_path = os.path.join(".claude", "skills", "capture-insight")
if skill_path not in sys.path:
    sys.path.append(skill_path)

# Import the helper from your local client
try:
    from supabase_client import list_topics
except ImportError:
    def list_topics(): return [] # Fallback if file not found

load_dotenv()

# --- GLOBAL STATE ---
current_topic = "General Research"
seen_messages = set() # To prevent double-printing "Vault Updated"

def print_menu():
    """Prints the status and instructions clearly to the terminal."""
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
    """Processes messages, avoids duplicates, and shows Confluence links."""
    global seen_messages
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    # Only print execution logs for background transparency
                    print(f"[System]: Executing {block.name}...")
                
                elif isinstance(block, TextBlock):
                    text = block.text.strip()
                    if not text: continue

                    # FIX: Logic to prevent double "Vault Updated" and show Confluence URLs
                    if "Vault Updated" in text:
                        if text not in seen_messages:
                            print(f"Agent: {text}")
                            seen_messages.add(text)
                    elif "http" in text or "Published" in text or "atlassian.net" in text:
                        print(f"\n🚀 SUCCESS: {text}")
                    else:
                        print(f"Agent: {text}")
    
    # Reset seen messages for the next interaction
    seen_messages.clear()
    print_menu()

async def clipboard_listener(client):
    """Background task: Watches clipboard and applies Topic Lock."""
    global current_topic
    last_clip = pyperclip.paste().strip()
    
    while True:
        try:
            current_clip = pyperclip.paste().strip()
            if current_clip and current_clip != last_clip:
                last_clip = current_clip
                print(f"\n[Raw Capture]: {current_clip[:60]}...")
                
                # Prepend the Topic Lock to the capture query
                query_text = f"TOPIC: {current_topic} | Raw capture: '{current_clip}'. Save as-is."
                await client.query(query_text)
                asyncio.create_task(handle_agent_responses(client))
            await asyncio.sleep(0.5)
        except Exception:
            await asyncio.sleep(1)

async def user_input_loop(client):
    """Foreground task: Handles commands and topic changes."""
    global current_topic
    while True:
        try:
            user_text = await asyncio.to_thread(input, "You: ")
            
            if not user_text.strip():
                continue

            # 1. TOPIC LISTER
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

            # 2. TOPIC SWITCHER (Flexible: supports '/topic ', '/ ', or just '/')
            if user_text.startswith("/topic ") or user_text.startswith("/ ") or user_text.startswith("/"):
                # Extract topic name by removing common command prefixes
                new_topic = user_text.replace("/topic ", "").replace("/ ", "")
                if new_topic.startswith("/"):
                    new_topic = new_topic[1:]
                
                current_topic = new_topic.strip()
                print(f"\n[System]: Topic updated and locked to: {current_topic}")
                print_menu()
                continue

            # 3. PUBLISHING LOGIC
            if "I am done" in user_text or "Publish" in user_text:
                publish_query = f"I am done. Publish all research notes for the topic '{current_topic}' to Confluence."
                await client.query(publish_query)
            else:
                # Standard questions or instructions
                await client.query(user_text)
            
            await handle_agent_responses(client)

        except Exception as e:
            print(f"Input Error: {e}")

async def main():
    # GIT-READY: Load path from .env or fallback to 'claude' for cross-platform support
    env_cli_path = os.getenv("CLAUDE_CLI_PATH", "claude")
    
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        cli_path=env_cli_path,
        cwd="./",
        setting_sources=["project"],
        allowed_tools=["Skill", "Bash", "Read", "Write"]
    )

    print("\n(venv) InsightVault: Power Research Mode Active.")
    print_menu()

    async with ClaudeSDKClient(options=options) as client:
        await asyncio.gather(
            clipboard_listener(client),
            user_input_loop(client)
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession ended. Your insights are safe in the vault.")