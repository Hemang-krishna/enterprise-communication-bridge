import os
import json
from typing import Dict, Any, List, Optional
from slack_integration import SlackIntegrationEngine
from notion_integration import NotionEnterpriseEngine

class EnterpriseCommunicationBridge:
    """
    Unified Bridge orchestrating Enterprise Communication & Workflows between
    Slack (messaging/announcements) and Notion (database/documentation).
    """

    def __init__(self, slack_engine: Optional[SlackIntegrationEngine] = None, notion_engine: Optional[NotionEnterpriseEngine] = None):
        self.slack = slack_engine or SlackIntegrationEngine()
        self.notion = notion_engine or NotionEnterpriseEngine()

    def dispatch_leader_instruction(self, leader_name: str, instruction: str, target_team_member: str, priority: str = "High") -> Dict[str, Any]:
        """
        Processes a command from the Main Project Leader:
        1. Logs the task into Notion Task Database assigned to the target team member.
        2. Formats and sends a Slack message notifying the team.
        """
        # Step 1: Create Task in Notion
        notion_res = self.notion.create_notion_task(
            title=instruction,
            assignee=target_team_member,
            priority=priority,
            status="In Progress"
        )

        # Step 2: Format & Send Slack Notification
        slack_text = (
            f"👑 *Instruction from Project Leader ({leader_name})*\n"
            f"🎯 *Task Assigned To:* {target_team_member}\n"
            f"⚡ *Priority:* `{priority}`\n"
            f"📌 *Instruction Details:* {instruction}\n"
            f"📂 *Notion Task ID:* `{notion_res['notion_task']['id']}`"
        )
        slack_res = self.slack.send_webhook_message(slack_text)

        return {
            "status": "DISPATCHED",
            "leader": leader_name,
            "instruction": instruction,
            "target_member": target_team_member,
            "notion_record": notion_res,
            "slack_delivery": slack_res
        }

    def publish_enterprise_documentation(self, title: str, category: str, author: str, content: str) -> Dict[str, Any]:
        """
        Publishes structured documentation:
        1. Creates a Notion Document Page in Knowledge Base.
        2. Broadcasts a documentation alert to Slack.
        """
        # Step 1: Publish to Notion
        doc_res = self.notion.publish_notion_document(
            title=title,
            category=category,
            author=author,
            markdown_content=content
        )

        # Step 2: Slack Announcement
        slack_text = (
            f"📚 *New Enterprise Documentation Published*\n"
            f"📄 *Title:* {title}\n"
            f"🏷️ *Category:* `{category}` | *Author:* {author}\n"
            f"🔗 *Notion Doc ID:* `{doc_res['notion_doc']['id']}`"
        )
        slack_res = self.slack.send_webhook_message(slack_text)

        return {
            "status": "PUBLISHED",
            "notion_record": doc_res,
            "slack_delivery": slack_res
        }

    def get_full_workspace_status(self) -> Dict[str, Any]:
        """Returns unified status across Slack and Notion platforms."""
        notion_overview = self.notion.get_workspace_overview()
        return {
            "slack_status": "ACTIVE" if self.slack.webhook_url or self.slack.bot_token else "STAGED",
            "notion_workspace": notion_overview,
            "system_health": "ENTERPRISE_OPERATIONAL"
        }


if __name__ == "__main__":
    bridge = EnterpriseCommunicationBridge()
    dispatch = bridge.dispatch_leader_instruction(
        leader_name="Dxrk sky .",
        instruction="Deploy new landing page and conduct user testing",
        target_team_member="Devin Digital Worker",
        priority="High"
    )
    print("Dispatch Result:", json.dumps(dispatch, indent=2))
