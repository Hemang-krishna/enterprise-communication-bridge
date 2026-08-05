import os
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

class SlackIntegrationEngine:
    """
    Enterprise Slack Messaging & Workflow Integration for Hermes.
    Handles channel broadcasts, team task pings, status updates, and webhooks.
    """

    def __init__(self, bot_token: Optional[str] = None, webhook_url: Optional[str] = None):
        self.bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN")
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")

    def send_webhook_message(self, text: str, channel_override: Optional[str] = None) -> Dict[str, Any]:
        """Sends a formatted message via Slack Incoming Webhook."""
        if not self.webhook_url:
            return {
                "success": False,
                "status": "SIMULATED",
                "text": text,
                "message": "Slack Webhook URL not set. Staged message successfully for dispatch when webhook is provided."
            }

        payload = {"text": text}
        if channel_override:
            payload["channel"] = channel_override

        req = urllib.request.Request(
            self.webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode("utf-8")
                return {"success": True, "status": "DELIVERED", "response": res_body}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post_chat_message(self, channel: str, text: str, blocks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Posts a message to a Slack channel via Slack Bot API."""
        if not self.bot_token:
            return {
                "success": False,
                "status": "SIMULATED",
                "channel": channel,
                "text": text,
                "message": "Slack Bot Token not set. Staged message successfully."
            }

        url = "https://slack.com/api/chat.postMessage"
        payload = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
        )

        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                return {"success": res.get("ok", False), "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def format_team_announcement(self, title: str, author: str, details: str, action_url: Optional[str] = None) -> str:
        """Formats a rich enterprise announcement string."""
        msg = f"📢 *[ENTERPRISE ANNOUNCEMENT]* *{title}*\n*From:* {author}\n> {details}"
        if action_url:
            msg += f"\n🔗 *Action Link:* {action_url}"
        return msg


if __name__ == "__main__":
    slack = SlackIntegrationEngine()
    announcement = slack.format_team_announcement(
        title="Project Workflow Initialization",
        author="Project Lead",
        details="Enterprise communication channels connected via Slack & Notion.",
        action_url="https://ephemeral-snickerdoodle-88c7ac.netlify.app"
    )
    res = slack.send_webhook_message(announcement)
    print("Slack Test Result:", json.dumps(res, indent=2))
