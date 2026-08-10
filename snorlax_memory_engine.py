import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

MEMORY_FILE = "/data/snorlax_memory.json"

class SnorlaxMemoryEngine:
    """
    Persistent Memory Store for Snorlax Bot (similar to Hermes persistent memory).
    Stores team preferences, project facts, directives, and interaction logs across turns.
    """

    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.memory = self.load_memory()

    def load_memory(self) -> Dict[str, Any]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"[Snorlax Memory Load Error]: {e}")
        
        return {
            "facts": [
                "Project Founder: Vishwajith (@Vish7781)",
                "Director in Technology: Monkey D Luffy (@lo_uffy_1999)",
                "Director of HR & Corporate Communications: Venky (@Dragoz666)",
                "Workspace Owner: Dxrk sky",
                "Rule: Snorlax must ALWAYS run real-time web searches and return exact answers with clickable source links.",
                "Rule: Never output static placeholder templates for unrelated questions.",
                "Rule: Respond warmly with cute emojis on @mentions.",
                "Rule: Send personal team workflow state reports directly to Dxrk sky on Telegram."
            ],
            "directives": [],
            "user_preferences": {},
            "last_updated": datetime.utcnow().isoformat()
        }

    def save_memory(self):
        try:
            self.memory["last_updated"] = datetime.utcnow().isoformat()
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logging.error(f"[Snorlax Memory Save Error]: {e}")

    def add_fact(self, fact: str):
        if fact not in self.memory["facts"]:
            self.memory["facts"].append(fact)
            self.save_memory()

    def get_memory_context(self) -> str:
        return "\n".join([f"• {f}" for f in self.memory["facts"]])

if __name__ == "__main__":
    mem = SnorlaxMemoryEngine()
    print("Snorlax Memory Loaded Successfully:")
    print(mem.get_memory_context())
