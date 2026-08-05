import unittest
import os
import json
from slack_integration import SlackIntegrationEngine
from notion_integration import NotionEnterpriseEngine
from enterprise_bridge import EnterpriseCommunicationBridge

class TestEnterpriseBridge(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = "/tmp/test_notion_db"
        self.notion = NotionEnterpriseEngine(local_storage_dir=self.tmp_dir)
        self.slack = SlackIntegrationEngine()
        self.bridge = EnterpriseCommunicationBridge(slack_engine=self.slack, notion_engine=self.notion)

    def test_slack_formatting(self):
        msg = self.slack.format_team_announcement("Test Title", "Lead", "Details")
        self.assertIn("Test Title", msg)
        self.assertIn("Lead", msg)

    def test_notion_task_creation(self):
        res = self.notion.create_notion_task(
            title="Unit Test Task",
            assignee="Test Member",
            priority="High",
            status="Todo"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["notion_task"]["title"], "Unit Test Task")

    def test_notion_doc_publishing(self):
        res = self.notion.publish_notion_document(
            title="Unit Test Doc",
            category="Test",
            author="Tester",
            markdown_content="# Test Content"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["notion_doc"]["title"], "Unit Test Doc")

    def test_bridge_dispatch_instruction(self):
        res = self.bridge.dispatch_leader_instruction(
            leader_name="Main Leader",
            instruction="Execute task immediately",
            target_team_member="Hermes Agent",
            priority="High"
        )
        self.assertEqual(res["status"], "DISPATCHED")
        self.assertEqual(res["target_member"], "Hermes Agent")

    def test_bridge_full_workspace_status(self):
        status = self.bridge.get_full_workspace_status()
        self.assertEqual(status["system_health"], "ENTERPRISE_OPERATIONAL")
        self.assertIn("notion_workspace", status)

if __name__ == "__main__":
    unittest.main()
