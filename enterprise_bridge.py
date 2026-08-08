import os
import json
from typing import Dict, Any, List, Optional
from discord_integration import DiscordIntegrationEngine
from notion_integration import NotionEnterpriseEngine

class EnterpriseCommunicationBridge:
    """
    Unified Bridge orchestrating Enterprise Communication & Workflows between
    Discord (messaging/announcements/embeds) and Notion (database/documentation).
    Slack has been completely replaced with Discord.
    """

    def __init__(self, discord_engine: Optional[DiscordIntegrationEngine] = None, notion_engine: Optional[NotionEnterpriseEngine] = None):
        self.discord = discord_engine or DiscordIntegrationEngine()
        self.notion = notion_engine or NotionEnterpriseEngine()

    def dispatch_leader_instruction(self, leader_name: str, instruction: str, target_team_member: str, priority: str = "High", channel_id_or_webhook: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a command from the Main Project Leader:
        1. Logs the task into Notion Task Database assigned to the target team member.
        2. Formats and dispatches a rich Discord embed card to the team channel.
        """
        # Step 1: Create Task in Notion
        notion_res = self.notion.create_notion_task(
            title=instruction,
            assignee=target_team_member,
            priority=priority,
            status="In Progress"
        )

        # Step 2: Format & Send Discord Embed Notification
        title = f"👑 Instruction from Leader ({leader_name})"
        desc = (
            f"**Target Member:** {target_team_member}\n"
            f"**Priority:** `{priority}`\n"
            f"**Details:** {instruction}\n"
            f"**Notion Task ID:** `{notion_res['notion_task']['id']}`"
        )
        fields = [
            {"name": "Assigned To", "value": target_team_member, "inline": True},
            {"name": "Priority", "value": priority, "inline": True},
            {"name": "Notion ID", "value": notion_res['notion_task']['id'], "inline": True}
        ]

        discord_res = self.discord.post_webhook_embed(
            title=title,
            description=desc,
            fields=fields,
            color=0x2563eb, # Royal Blue
            webhook_url=channel_id_or_webhook
        )

        return {
            "status": "DISPATCHED",
            "leader": leader_name,
            "instruction": instruction,
            "target_member": target_team_member,
            "notion_record": notion_res,
            "discord_delivery": discord_res
        }

    def publish_enterprise_documentation(self, title: str, category: str, author: str, content: str, channel_id_or_webhook: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes structured documentation:
        1. Creates a Notion Document Page in Knowledge Base.
        2. Broadcasts a documentation alert embed to Discord.
        """
        # Step 1: Publish to Notion
        doc_res = self.notion.publish_notion_document(
            title=title,
            category=category,
            author=author,
            markdown_content=content
        )

        # Step 2: Discord Announcement
        embed_title = f"📚 New Enterprise Documentation: {title}"
        desc = f"**Category:** `{category}` | **Author:** {author}\n**Notion Doc ID:** `{doc_res['notion_doc']['id']}`"
        fields = [
            {"name": "Category", "value": category, "inline": True},
            {"name": "Author", "value": author, "inline": True}
        ]

        discord_res = self.discord.post_webhook_embed(
            title=embed_title,
            description=desc,
            fields=fields,
            color=0x10b981, # Emerald Green
            webhook_url=channel_id_or_webhook
        )

        return {
            "status": "PUBLISHED",
            "notion_record": doc_res,
            "discord_delivery": discord_res
        }

    def add_team_member(self, name: str, role: str, email: str, discord_id: Optional[str] = None) -> Dict[str, Any]:
        """Adds a team member to Notion and sends a welcome alert embed to Discord."""
        notion_res = self.notion.add_team_member(name=name, role=role, email=email, discord_id=discord_id)
        
        embed_title = f"👤 New Team Member Added: {name}"
        desc = f"**Name:** {name}\n**Role:** `{role}`\n**Email:** `{email}`\n**Notion Team Record:** Logged in 'Anya's Space'"
        fields = [
            {"name": "Name", "value": name, "inline": True},
            {"name": "Role", "value": role, "inline": True},
            {"name": "Email", "value": email, "inline": True}
        ]
        
        discord_res = self.discord.post_webhook_embed(title=embed_title, description=desc, fields=fields, color=0x8b5cf6)
        return {"status": "MEMBER_ADDED", "notion_record": notion_res, "discord_delivery": discord_res}

    def get_full_workspace_status(self) -> Dict[str, Any]:
        """Returns unified status across Discord and Notion platforms."""
        notion_overview = self.notion.get_workspace_overview()
        return {
            "discord_status": "ACTIVE" if self.discord.webhook_url or self.discord.bot_token else "STAGED",
            "notion_workspace": notion_overview,
            "system_health": "DISCORD_NOTION_ENTERPRISE_OPERATIONAL"
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
