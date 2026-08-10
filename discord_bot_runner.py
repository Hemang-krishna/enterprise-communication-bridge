import os
import sys
import json
import asyncio
import logging
import urllib.request
import urllib.parse
import re
import random
from datetime import datetime
from bs4 import BeautifulSoup

sys.path.append("/data/integrations")
sys.path.append("/data")

import discord
from discord.ext import commands, tasks
from integrations.enterprise_bridge import EnterpriseCommunicationBridge
from integrations.snorlax_memory_engine import SnorlaxMemoryEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "1535612387111997512")
CHAT_LOG_FILE = "/data/discord_team_chats.json"
TELEGRAM_REPORT_FILE = "/data/reports/telegram_team_workflow_report.txt"

if not BOT_TOKEN and os.path.exists("/data/.env"):
    with open("/data/.env", "r") as f:
        for line in f:
            if line.startswith("DISCORD_BOT_TOKEN="):
                BOT_TOKEN = line.strip().split("=", 1)[1]
            elif line.startswith("DISCORD_CHANNEL_ID="):
                CHANNEL_ID = line.strip().split("=", 1)[1]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
bridge = EnterpriseCommunicationBridge()
snorlax_mem = SnorlaxMemoryEngine()

CUTE_EMOJIS = ["😴", "⚡", "🌸", "🎀", "🐣", "🔮", "☕", "🎨", "🌟", "✨", "🐾", "🐥"]

GREETING_RESPONSES = [
    "Hii {user}! 🌸✨ Hope you're having an awesome and high-energy day on Project Snorlax! How can I help you or power your workflow right now? ☕⚡",
    "Hey {user}! 😴✨ Snorlax is here and active 24/7 with persistent memory! What are we building or automating today? 🔮🎨",
    "Hello {user}! 🐣🎀 Great to see you in the chat! Let me know if you need any web research, Notion task updates, or memory recalls! ⚡✨"
]

def perform_bulletproof_web_search(query: str, limit: int = 4) -> list:
    """Extracts real-time web search results (titles, snippets, and clean clickable links)."""
    encoded = urllib.parse.quote(query)
    url = "https://lite.duckduckgo.com/lite/"
    req = urllib.request.Request(
        url,
        data=f"q={encoded}".encode("utf-8"),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    results = []
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.find_all("tr")
            for i in range(0, len(rows) - 1):
                title_a = rows[i].find("a", class_="result-link")
                snippet_td = rows[i+1].find("td", class_="result-snippet")
                if title_a and snippet_td:
                    link = title_a.get("href", "")
                    if "//duckduckgo.com/l/?uddg=" in link:
                        link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                    elif link.startswith("//"):
                        link = "https:" + link
                    
                    clean_title = title_a.get_text().strip()
                    clean_snippet = snippet_td.get_text().strip()
                    
                    if clean_title and clean_snippet:
                        results.append({
                            "title": clean_title,
                            "link": link,
                            "snippet": clean_snippet
                        })
    except Exception as e:
        logging.error(f"[Bulletproof Search Error]: {e}")

    return results[:limit]

def log_team_chat_message(author: str, content: str, channel: str):
    os.makedirs("/data/reports", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "author": str(author),
        "content": content,
        "channel": channel
    }
    data = []
    if os.path.exists(CHAT_LOG_FILE):
        try:
            with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append(entry)
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@bot.event
async def on_ready():
    logging.info(f"⚡ [Snorlax Bot Online] Authenticated as {bot.user} (ID: {bot.user.id})")
    print(f"✅ Snorlax Autonomous Bot Online 24/7! Persistent Memory Engine Active.")
    await bot.change_presence(activity=discord.Game(name="24/7 Persistent Memory & Live Search"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content_raw = message.content.strip()
    if content_raw:
        log_team_chat_message(author=message.author, content=content_raw, channel=str(message.channel))

    is_mentioned = bot.user.mentioned_in(message)
    is_prefixed = message.content.startswith("!snorlax") or message.content.startswith("!anya") or message.content.startswith("!hermes")

    if is_mentioned or is_prefixed:
        content_clean = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if content_clean.startswith("!snorlax") or content_clean.startswith("!anya") or content_clean.startswith("!hermes"):
            content_clean = content_clean.split(" ", 1)[1] if " " in content_clean else ""

        query_clean = content_clean.strip()
        user_display = message.author.display_name
        cute_icon = random.choice(CUTE_EMOJIS)

        # Command: Save Fact to Snorlax Persistent Memory
        if query_clean.lower().startswith("remember") or "save memory" in query_clean.lower():
            fact_to_save = re.sub(r'^(remember|save memory|remember that)\s+', '', query_clean, flags=re.IGNORECASE).strip()
            snorlax_mem.add_fact(f"Directive from {user_display}: {fact_to_save}")
            embed = discord.Embed(
                title=f"🧠 Snorlax Persistent Memory Saved",
                description=f"Hii **{message.author.mention}** {cute_icon}! I have saved this fact to my persistent memory vault (`/data/snorlax_memory.json`):\n\n📌 **Saved Memory:** `{fact_to_save}`",
                color=0x8b5cf6
            )
            await message.channel.send(embed=embed)
            return

        # Command: Memory Inspection
        elif query_clean.lower() in ["memory", "show memory", "facts"]:
            mem_text = snorlax_mem.get_memory_context()
            embed = discord.Embed(
                title=f"🧠 Snorlax Persistent Memory Vault",
                description=f"Here are my current persistent facts and project rules:\n\n{mem_text}",
                color=0x8b5cf6
            )
            await message.channel.send(embed=embed)
            return

        # Command: Simple Greetings
        elif query_clean.lower() in ["hii", "hi", "hello", "hey", "sup", "yo"]:
            greeting_msg = random.choice(GREETING_RESPONSES).format(user=message.author.mention)
            await message.channel.send(greeting_msg)
            return

        # Command: Status
        elif query_clean.lower() == "status":
            embed = discord.Embed(
                title=f"{cute_icon} Snorlax System Status",
                description="**Status:** 100% Operational (24/7)\n**Persistent Memory Engine:** ACTIVE (`snorlax_memory.json`)\n**Live Web Search:** Bulletproof BeautifulSoup Engine Active",
                color=0x2563eb
            )
            await message.channel.send(embed=embed)
            return

        # DYNAMIC SEARCH & ANSWER ENGINE WITH PERSISTENT MEMORY & EXACT RESULTS
        else:
            search_term = re.sub(r'^(tell me|search|research|find|look up|what is|how to)\s+', '', query_clean, flags=re.IGNORECASE).strip()
            if not search_term:
                search_term = query_clean

            async with message.channel.typing():
                web_results = perform_bulletproof_web_search(search_term, limit=4)

            is_ai_automation_query = any(kw in query_clean.lower() for kw in ["ai automation", "n8n", "flow architect", "workflow diagram"])

            if is_ai_automation_query:
                easy_definition = (
                    "An **AI Automation** is an autonomous digital pipeline that combines Large Language Models (LLMs) with deterministic workflow nodes (n8n, webhooks, databases, and APIs) to read unstructured data and execute tasks automatically."
                )
                visual_flow_diagram = (
                    "```text\n"
                    "[ Node 1: Webhook Trigger ] ⚡ ➔ [ Node 2: Gemini / Ollama LLM ] 🧠 ➔ [ Node 3: Qdrant Vector RAG ] 🔮 ➔ [ Node 4: Discord Alert ] 🛸\n"
                    "```"
                )
                embed = discord.Embed(
                    title=f"{cute_icon} {user_display}'s AI Automation Query Answer",
                    description=f"Hey **{message.author.mention}** {cute_icon}!\n\n### 🧠 What is an AI Automation?\n{easy_definition}\n\n### 🔌 Visual n8n Flow Architect Diagram\n{visual_flow_diagram}\n👉 **[Launch Personal Snorlax AI User Interface](https://anya-agentic-space.loca.lt/static/snorlax_personal_ui.html)**",
                    color=0x10b981
                )
            else:
                embed = discord.Embed(
                    title=f"🔍 {user_display}'s Research Answer: {search_term[:80]}",
                    description=f"Hello **{message.author.mention}** {cute_icon}! Here are the real-time live web search findings for your request:\n\n💬 **Query:** `{query_clean}`",
                    color=0x10b981
                )

            # APPEND EXTRACTED WEB RESULTS & CLICKABLE DIRECT LINKS
            if web_results:
                sources_text = ""
                for idx, res in enumerate(web_results, 1):
                    sources_text += f"**{idx}. {res['title'][:100]}**\n{res['snippet'][:250]}\n🔗 **[Open Source Link]({res['link']})**\n\n"
                
                embed.add_field(
                    name="🌐 Live Web Search Findings & Exact Sources",
                    value=sources_text[:1000],
                    inline=False
                )

            embed.set_footer(text=f"Project Snorlax • Persistent Memory & Search Active 24/7 {cute_icon}")
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found.")
        sys.exit(1)
    
    print("Starting 24/7 Snorlax Bot with Persistent Memory Engine & Live Search...")
    bot.run(BOT_TOKEN)
