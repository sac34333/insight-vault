---
name: capture-insight
description: Captures any text snippet, highlight, or note and saves it exactly as provided to the Supabase vault and Confluence. Use this for general reading notes, research, or code.
---
# InsightVault Protocol: Raw Capture Mode

## 1. Minimal Processing
* **No Summarization**: Do not summarize or alter the user's text. 
* **Topic Assignment**: 
    * Use the current session topic. 
    * Default to **"General Research"** if unknown. 
    * Never ask the user for a topic unless the clipboard is empty.

## 2. Direct Storage (Supabase)
* **Immediate Action**: Call `insert_row` into the `reading_notes` table immediately.
* **Data Mapping**:
    * `content`: The **exact raw text** provided by the user.
    * `topic`: The current or default topic.
    * `insight_tag`: A 3-5 word label (e.g., "Note on [Topic]") to keep tokens low.
* **Confirmation**: Print only: "Vault Updated 🔒 [{topic}]".

## 3. Raw Export (Confluence)
## 3. Raw Export (Confluence)
* **Trigger**: Activate only on "I am done" or "Publish research".
* **Aggregation**: Query the `reading_notes` table for entries where the `topic` matches the **specific topic provided in the user's command**. Do not fetch notes for any other topics.
* **Format**: Do not synthesize. List the snippets exactly as they were captured, separated by horizontal rules (---) and Markdown headers for dates/times if available.
* **Publish**: Use the `confluence` tool (`create_page`) to post the raw collection to the **InsightVau** space.

## Constraints
* **Ultra-Low Tokens**: Do not analyze value or provide commentary. Move directly to tool execution.
* **Preservation**: The integrity of the original snippet is the priority. Do not fix grammar or rephrase.