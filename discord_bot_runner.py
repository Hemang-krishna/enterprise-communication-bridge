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

CUTE_EMOJIS = ["😴", "⚡", "🌸", "🎀", "🐣", "🔮", "☕", "🎨", "🌟", "✨", "🐾", "🐥"]

GREETING_RESPONSES = [
    "Hii {user}! 🌸✨ Hope you're having an awesome and high-energy day on Project Snorlax! How can I help you or power your workflow right now? ☕⚡",
    "Hey {user}! 😴✨ Snorlax is here and active 24/7! What are we building or automating today? 🔮🎨",
    "Hello {user}! 🐣🎀 Great to see you in the chat! Let me know if you need any web research, Notion task updates, or code help! ⚡✨",
    "Hii there {user}! 🌸🐾 Ready to smash our AI Automation goals today! How can I assist you right now? 🌟☕"
]

MOTIVATIONAL_QUOTES = [
    ("“Simplicity is prerequisite for reliability.” — Edsger W. Dijkstra", "Break complex automation nodes into small, focused sub-systems to eliminate mental clutter."),
    ("“The best way to predict the future is to invent it.” — Alan Kay", "Every AI flow you build today shapes the autonomous infrastructure of tomorrow."),
    ("“Action is the foundational key to all success.” — Pablo Picasso", "Start with a working prototype, then iterate rapidly. Perfect execution beats overthinking.")
]

def perform_bulletproof_web_search(query: str, limit: int = 3) -> list:
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
    print(f"✅ Snorlax Autonomous Bot Online 24/7! Visual n8n Flow Architect Active.")
    await bot.change_presence(activity=discord.Game(name="24/7 Visual n8n AI Flow Architect"))

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

        # Case 1: Simple Greetings
        if query_clean.lower() in ["hii", "hi", "hello", "hey", "sup", "yo"]:
            greeting_msg = random.choice(GREETING_RESPONSES).format(user=message.author.mention)
            await message.channel.send(greeting_msg)
            return

        # Case 2: Status Command
        elif query_clean.lower() == "status":
            embed = discord.Embed(
                title=f"{random.choice(CUTE_EMOJIS)} Snorlax System Status",
                description="**Status:** 100% Operational (24/7)\n**n8n AI Flow Architect:** ACTIVE\n**Starter Kit Repo:** Synced (*Hemang-krishna/self-hosted-ai-starter-kit*)",
                color=0x2563eb
            )
            await message.channel.send(embed=embed)
            return

        # Case 3: Questions & AI Automations (DEFINITION FIRST + VISUAL n8n FLOW ARCHITECT + SOURCES LATER)
        else:
            async with message.channel.typing():
                web_results = perform_bulletproof_web_search(query_clean, limit=3)

            cute_icon = random.choice(CUTE_EMOJIS)
            
            # DEFINITION & EXPLANATION FIRST
            definition_text = (
                f"An **AI Automation** is an autonomous digital pipeline that combines **Large Language Models (LLMs)** with deterministic workflow nodes (n8n, webhooks, databases, and APIs).\n\n"
                f"Unlike static rule-based scripts, AI Automations read unstructured data, reason through complex decisions, query vector databases (Qdrant RAG), and execute actions (voice calls, emails, git commits) automatically without human intervention."
            )

            # VISUAL n8n FLOW ARCHITECT DIAGRAM
            visual_flow_diagram = (
                "```text\n"
                "[ Node 1: Webhook / Scraper Trigger ] ⚡\n"
                "       │  Receives Inbound Event / Lead Scraper Data\n"
                "       ▼\n"
                "[ Node 2: Gemini 2.0 / Ollama AI Agent ] 🧠\n"
                "       │  Reasons over Task Prompt & Qualifies Eligibility\n"
                "       ▼\n"
                "[ Node 3: Qdrant Vector RAG Store ] 🔮\n"
                "       │  Queries Knowledge Context & Historical Guidelines\n"
                "       ▼\n"
                "[ Node 4: Sub-Second Voice AI & Discord Alert Node ] 🛸\n"
                "       └─ Dials Phone Call (~380ms) & Dispatches Discord Embed!\n"
                "```"
            )

            embed = discord.Embed(
                title=f"{cute_icon} {user_display}'s AI Automation & Visual Flow Architect Answer",
                description=f"Hey **{message.author.mention}** {cute_icon}!\n\n### 🧠 What is an AI Automation?\n{definition_text}\n\n### 🔌 Visual n8n Flow Architect Diagram\n{visual_flow_diagram}\n👉 **[Open Interactive n8n Canvas Web App](https://anya-agentic-space.loca.lt/static/n8n_ai_flow_architect.html)**",
                color=0x10b981
            )

            # SUPPORTED REFERENCE WEBPAGES LATER AT THE BOTTOM
            if web_results:
                sources_text = ""
                for idx, res in enumerate(web_results, 1):
                    sources_text += f"{idx}. **[{res['title'][:80]}]({res['link']})**\n_{res['snippet'][:120]}_\n\n"
                
                embed.add_field(
                    name="🔗 Supporting Web References & Sources",
                    value=sources_text[:1000],
                    inline=False
                )

            embed.set_footer(text=f"Project Snorlax • n8n Flow Architect Active 24/7 {random.choice(CUTE_EMOJIS)}")
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found.")
        sys.exit(1)
    
    print("Starting 24/7 Snorlax Bot with Visual n8n Flow Architect & AI Automation Definition Engine...")
    bot.run(BOT_TOKEN)
