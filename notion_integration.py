import os
import json
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")

class NotionEnterpriseEngine:
    """
    Enterprise Notion Workspace Engine for Hermes.
    Manages Tasks & Roadmap Databases, Documentation Knowledge Base,
    and Team Member Role Specifications.
    """

    def __init__(self, api_key: Optional[str] = None, local_storage_dir: str = "/data/integrations/notion_local_db"):
        self.api_key = api_key or os.environ.get("NOTION_API_KEY") or NOTION_TOKEN
        self.local_dir = local_storage_dir
        os.makedirs(local_storage_dir, exist_ok=True)
        
        self.tasks_file = os.path.join(local_storage_dir, "tasks_database.json")
        self.docs_file = os.path.join(local_storage_dir, "docs_database.json")
        self.team_file = os.path.join(local_storage_dir, "team_database.json")

        self._init_local_databases()

    def _init_local_databases(self):
        if not os.path.exists(self.tasks_file):
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump({"database_title": "Enterprise Project Roadmap & Tasks", "items": []}, f, indent=2)

        if not os.path.exists(self.docs_file):
            with open(self.docs_file, "w", encoding="utf-8") as f:
                json.dump({"database_title": "Enterprise Documentation & Knowledge Base", "items": []}, f, indent=2)

        if not os.path.exists(self.team_file):
            default_team = {
                "database_title": "Enterprise Team Directory",
                "workspace_owner": "project.anyaforger@gmail.com",
                "members": [
                    {"name": "Project Lead (Dxrk sky)", "email": "project.anyaforger@gmail.com", "role": "Workspace Owner", "status": "ACTIVE"},
                    {"name": "Hermes AI Agent", "role": "Chief Operating & Technical Agent", "status": "ACTIVE"},
                    {"name": "SDR Digital Worker (Alice)", "role": "Lead Generation & Outreach", "status": "ACTIVE"},
                    {"name": "Sierra Digital Worker", "role": "Customer Support & Action Engine", "status": "ACTIVE"},
                    {"name": "Devin Digital Worker", "role": "Autonomous Software Engineer", "status": "ACTIVE"}
                ]
            }
            with open(self.team_file, "w", encoding="utf-8") as f:
                json.dump(default_team, f, indent=2)

    def search_connected_pages(self) -> List[Dict[str, Any]]:
        """Searches for Notion pages that have been shared with Anya's connection."""
        req = urllib.request.Request(
            "https://api.notion.com/v1/search",
            data=json.dumps({"query": ""}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res.get("results", [])
        except Exception as e:
            return []

    def create_notion_task(self, title: str, assignee: str, priority: str, status: str, due_date: Optional[str] = None) -> Dict[str, Any]:
        """Creates a project task in the task database."""
        item = {
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "title": title,
            "assignee": assignee,
            "priority": priority, # High, Medium, Low
            "status": status,     # Todo, In Progress, Review, Completed
            "due_date": due_date or datetime.now().strftime("%Y-%m-%d")
        }

        # Store in local Notion DB mirror
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["items"].append(item)
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Check if live Notion page is connected
        connected_pages = self.search_connected_pages()
        live_sync_status = "LOCAL_STAGED"
        live_page_id = None

        if connected_pages:
            # Find task database or fallback to page
            target_db_id = None
            for p in connected_pages:
                if p.get("object") == "database":
                    target_db_id = p.get("id")
                    break
            
            if target_db_id:
                payload = {
                    "parent": {"database_id": target_db_id},
                    "properties": {
                        "Task Name": {
                            "title": [{"text": {"content": title}}]
                        },
                        "Status": {"select": {"name": status if status in ["Todo", "In Progress", "Review", "Completed"] else "Todo"}},
                        "Priority": {"select": {"name": priority if priority in ["High", "Medium", "Low"] else "Medium"}},
                        "Assignee": {"select": {"name": assignee}},
                        "Due Date": {"date": {"start": item["due_date"]}}
                    }
                }
            else:
                parent_id = connected_pages[0]["id"]
                payload = {
                    "parent": {"page_id": parent_id},
                    "properties": {
                        "title": {
                            "title": [{"text": {"content": f"Task: {title}"}}]
                        }
                    },
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": f"Assignee: {assignee} | Priority: {priority} | Status: {status} | Due: {item['due_date']}"}}
                                ]
                            }
                        }
                    ]
                }
            req = urllib.request.Request(
                "https://api.notion.com/v1/pages",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json"
                }
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    page_res = json.loads(resp.read().decode("utf-8"))
                    live_sync_status = "LIVE_SYNCED"
                    live_page_id = page_res.get("id")
            except Exception as e:
                live_sync_status = f"ERROR: {str(e)}"

        return {
            "success": True,
            "notion_task": item,
            "live_sync_status": live_sync_status,
            "live_page_id": live_page_id,
            "connected_pages_count": len(connected_pages)
        }

    def publish_notion_document(self, title: str, category: str, author: str, markdown_content: str) -> Dict[str, Any]:
        """Publishes structured documentation into the knowledge base."""
        doc = {
            "id": f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "title": title,
            "category": category,
            "author": author,
            "content": markdown_content
        }

        with open(self.docs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["items"].append(doc)
        with open(self.docs_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return {"success": True, "notion_doc": doc}

    def get_workspace_overview(self) -> Dict[str, Any]:
        """Returns complete overview of tasks, documentation, and team directory."""
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        with open(self.docs_file, "r", encoding="utf-8") as f:
            docs = json.load(f)
        with open(self.team_file, "r", encoding="utf-8") as f:
            team = json.load(f)

        return {
            "tasks": tasks,
            "docs": docs,
            "team": team,
            "connected_pages": self.search_connected_pages()
        }
