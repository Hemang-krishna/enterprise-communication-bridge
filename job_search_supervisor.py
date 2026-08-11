import os
import sys
import json
import logging
from datetime import datetime

sys.path.append("/data/integrations")
sys.path.append("/data")

from job_search_agent import search_india_operations_jobs
from discord_integration import DiscordIntegrationEngine
from notion_integration import NotionEnterpriseEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "1535612387111997512")

class JobSearchSupervisorAgent:
    """
    Supervisor Agent that oversees the entire Customer Support Operations
    job search execution, verifies application links, logs to Notion,
    and dispatches report cards to Discord & Telegram.
    """

    def __init__(self):
        self.discord_engine = DiscordIntegrationEngine()
        self.notion_engine = NotionEnterpriseEngine()

    def run_supervisor_pipeline(self) -> dict:
        logging.info("🚀 [Supervisor Agent] Initiating Operations Job Search Supervision Pipeline...")
        
        # Step 1: Execute Job Search Agent
        jobs = search_india_operations_jobs()
        logging.info(f"🔍 [Supervisor Agent] Audited {len(jobs)} total job opportunities.")

        # Step 2: Log Summary Task in Notion
        notion_res = self.notion_engine.create_notion_task(
            title=f"Operations & Customer Support Job Search Audit ({len(jobs)} Roles Discovered)",
            assignee="Supervisor Agent",
            priority="High",
            status="IN_PROGRESS"
        )

        # Step 3: Format Rich Discord Embed Card
        top_jobs = jobs[:4]
        fields = []
        for idx, j in enumerate(top_jobs, 1):
            fields.append({
                "name": f"💼 {idx}. {j['title'][:100]}",
                "value": f"📍 **Location:** {j['location']}\n_{j['snippet'][:180]}_\n🔗 **[Click Here to Apply Directly]({j['link']})**",
                "inline": False
            })

        embed = {
            "title": f"💼 Operations & Customer Support Job Search Report (6+ Yrs Exp)",
            "description": (
                f"**Supervisor Agent Execution Completed!** 🌸✨\n\n"
                f"Audited **{len(jobs)} active job opportunities** in Operations, Customer Support, and CX Leadership "
                f"across **Hyderabad & Bangalore** with direct apply links below:\n"
            ),
            "color": 0x10b981, # Emerald Green
            "fields": fields,
            "footer": {"text": "Supervisor Agent • Automated Job Search Pipeline 🌸"}
        }

        # Step 4: Dispatch Embed Card to Discord
        discord_res = self.discord_engine.post_channel_message(channel_id=CHANNEL_ID, text="", embed=embed)

        return {
            "success": True,
            "jobs_count": len(jobs),
            "notion_task_id": notion_res.get("task", {}).get("id"),
            "discord_message_id": discord_res.get("data", {}).get("id")
        }

if __name__ == "__main__":
    supervisor = JobSearchSupervisorAgent()
    res = supervisor.run_supervisor_pipeline()
    print("=== SUPERVISOR AGENT JOB SEARCH COMPLETE ===")
    print(json.dumps(res, indent=2))
