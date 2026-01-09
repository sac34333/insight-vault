🔒 InsightVault: Create notetaking application using Claude Agent Skills and SDK

InsightVault turns your clipboard into a structured, AI-powered database of your personal notes. It uses the Claude Agent SDK to listen for text you copy while browsing or reading and automatically tags, stores, and organizes it into a private vault. When you're done, it publishes a formatted report to Confluence with a single command. It is a functional demonstration of how to build real-world tools using the Claude Agent SDK. It showcases a "headless" agentic workflow where Claude is taught custom skills to bridge the gap between a local environment and cloud services like Supabase and Confluence.

🧠 Claude Agent SDK & Skills: How it Works

This project is built directly on the principles of the Claude Agent SDK and Claude Skills.

    - Claude Agent SDK: Acts as the orchestration layer. It provides the ClaudeSDKClient which allows our Python application to communicate with Claude, manage sessions, and handle tool execution loops.

    - Claude Skills: These are the modular units of capability. Following the official SDK documentation, a Skill consists of a Definition (written in natural language within a SKILL.md file) and an Implementation (executable code like Python or Bash). By registering these skills, we "teach" Claude how to perform specific tasks without hard-coded logic.

📂 Project Architecture (The SDK Logic)

The power of the Claude Agent SDK lies in its simplicity. Instead of building complex backends, we define Skills that Claude uses to interact with the world.

    - run_agent.py: The entry point. A lightweight script that initializes the ClaudeSDKClient and manages the OS-level clipboard listener.

    - .claude/skills/capture-insight/: A self-contained Claude Skill directory, structured according to SDK standards.

    - SKILL.md: The Skill Definition. This follows the Claude Skills structure by providing natural language instructions that map user intent to specific bash commands. It defines what the skill does and when Claude should use it.

    - supabase_client.py: A Skill Implementation script. This is the actual "tool" or resources Claude calls to perform database operations.

    - confluence_client.py: A Skill Implementation script. This tool allows the agent to interact with the Confluence API for final publishing.


The Workflow

This tool is designed for high-speed Note taking for various purposes. You don't need to switch between tabs or manually paste into documents.

    1. Lock a Topic: Tell the vault what you are reading or researching (e.g., /topic Agentic AI).

    2. Browse & Copy: Go to any website. Highlight text and press Ctrl+C.

    3. Auto-Capture: The Agent detects the copy in the background and saves it to your Supabase Database vault instantly.

    4. Publish: Type I am done to generate a formatted Confluence research page automatically.

🛠️ Setup Guide (5 Minutes)

    1. Prerequisites

    - Python 3.10+ installed.

    - Node.js (LTS) installed (required for the Claude Agent engine).

    - Claude Code CLI installed (npm install -g @anthropic-ai/claude-code).

2. Installation

# Clone the repository
git clone [https://github.com/your-username/insight-vault.git](https://github.com/your-username/insight-vault.git)
cd insight-vault

# Set up the virtual environment
python -m venv venv

# Activate the environment
# Windows:
.\venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt


3. Environment Configuration

# --- DATABASE (Supabase) ---
SUPABASE_URL=[https://your-project.supabase.co](https://your-project.supabase.co)
SUPABASE_KEY=your-anon-key

# --- DOCUMENTATION (Confluence) ---
CONFLUENCE_URL=[https://your-domain.atlassian.net](https://your-domain.atlassian.net)
CONFLUENCE_USER=your-email
CONFLUENCE_API_TOKEN=your-atlassian-api-token

# --- AGENT CONFIGURATION ---
# Windows: Provide the absolute path to your claude.cmd file
CLAUDE_CLI_PATH=C:\Users\YOUR_USERNAME\AppData\Roaming\npm\claude.cmd

# Mac / Linux: Usually 'claude' if in your PATH, or use the full path
# CLAUDE_CLI_PATH=claude


4. Run the Tool

python run_agent.py
