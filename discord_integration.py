import os
import json
import urllib.request
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

class DiscordIntegrationEngine:
    """
    Enterprise Discord Messaging & Workflow Integration for Hermes & Project Anya.
    Replaces Slack as primary enterprise team communication bridge.
    Handles channel broadcasts, rich embeds, Notion workspace sync, file uploads, and webhooks.
    """

    def __init__(self, bot_token: Optional[str] = None, webhook_url: Optional[str] = None):
        self.bot_token = bot_token or os.environ.get("DISCORD_BOT_TOKEN")
        if not self.bot_token and os.path.exists("/data/.env"):
            with open("/data/.env", "r") as f:
                for line in f:
                    if line.startswith("DISCORD_BOT_TOKEN="):
                        self.bot_token = line.strip().split("=", 1)[1]
                        break
        self.webhook_url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
        self.api_base = "https://discord.com/api/v10"

    def post_webhook_embed(self, title: str, description: str, fields: Optional[List[Dict[str, Any]]] = None, color: int = 0x2563eb, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Dispatches a rich colored embed card via Discord Incoming Webhook.
        """
        url = webhook_url or self.webhook_url
        if not url:
            return {
                "success": False,
                "status": "SIMULATED",
                "title": title,
                "description": description,
                "message": "Discord Webhook URL not set in env. Staged message successfully."
            }

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "footer": {"text": "Project Anya • Discord Integration Engine"}
        }
        if fields:
            embed["fields"] = fields

        payload = {"embeds": [embed]}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "DiscordBot (https://github.com/Hemang-krishna, 1.0)"
            }
        )

        try:
            with urllib.request.urlopen(req) as response:
                return {"success": True, "status": "DELIVERED", "code": response.status}
        except Exception as e:
            logging.error(f"[Discord Webhook Error]: {e}")
            return {"success": False, "error": str(e)}

    def post_channel_message(self, channel_id: str, text: str, embed: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Posts a text message or embed to a specific Discord Channel via Bot Token API.
        """
        if not self.bot_token:
            return {
                "success": False,
                "status": "SIMULATED",
                "channel_id": channel_id,
                "text": text,
                "message": "DISCORD_BOT_TOKEN not set in env."
            }

        url = f"{self.api_base}/channels/{channel_id}/messages"
        payload: Dict[str, Any] = {"content": text}
        if embed:
            payload["embeds"] = [embed]

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bot {self.bot_token}",
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "DiscordBot (https://github.com/Hemang-krishna, 1.0)"
            }
        )

        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                return {"success": True, "status": "DELIVERED", "data": res}
        except Exception as e:
            logging.error(f"[Discord API Error]: {e}")
            return {"success": False, "error": str(e)}

    def sync_notion_event_to_discord(self, task_title: str, status: str, priority: str, notion_url: str, channel_id_or_webhook: Optional[str] = None) -> Dict[str, Any]:
        """
        Formats and broadcasts a live Notion Task event to Discord.
        """
        title = f"📋 Notion Workspace Event: {task_title}"
        desc = f"**Task:** {task_title}\n**Status:** `{status}`\n**Priority:** `{priority}`\n🔗 [Open in Notion Workspace]({notion_url})"
        
        fields = [
            {"name": "Status", "value": status, "inline": True},
            {"name": "Priority", "value": priority, "inline": True},
            {"name": "Workspace", "value": "Anya's Space", "inline": True}
        ]

        if channel_id_or_webhook and channel_id_or_webhook.startswith("http"):
            return self.post_webhook_embed(title=title, description=desc, fields=fields, color=0x3b82f6, webhook_url=channel_id_or_webhook)
        elif channel_id_or_webhook:
            embed = {
                "title": title,
                "description": desc,
                "color": 0x3b82f6,
                "fields": fields,
                "footer": {"text": "Project Anya • Notion-Discord Bridge"}
            }
            return self.post_channel_message(channel_id=channel_id_or_webhook, text="", embed=embed)
        else:
            return self.post_webhook_embed(title=title, description=desc, fields=fields, color=0x3b82f6)

if __name__ == "__main__":
    discord_engine = DiscordIntegrationEngine()
    print("Discord Integration Engine Initialized.")
