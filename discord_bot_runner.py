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

# Warm natural greetings pool for simple team hellos
GREETING_RESPONSES = [
    "Hii {user}! 🌸✨ Hope you're having an awesome and high-energy day on Project Snorlax! How can I help you or power your workflow right now? ☕⚡",
    "Hey {user}! 😴✨ Snorlax is here and active 24/7! What are we building or automating today? 🔮🎨",
    "Hello {user}! 🐣🎀 Great to see you in the chat! Let me know if you need any web research, Notion task updates, or code help! ⚡✨",
    "Hii there {user}! 🌸🐾 Ready to smash our AI Automation goals today! How can I assist you right now? 🌟☕"
]

MOTIVATIONAL_QUOTES = [
    ("“Simplicity is prerequisite for reliability.” — Edsger W. Dijkstra", "Break complex automation nodes into small, focused sub-systems to eliminate mental clutter."),
    ("“The best way to predict the future is to invent it.” — Alan Kay", "Every AI flow you build today shapes the autonomous infrastructure of tomorrow."),
    ("“Action is the foundational key to all success.” — Pablo Picasso", "Start with a working prototype, then iterate rapidly. Perfect execution beats overthinking."),
    ("“It always seems impossible until it's done.” — Nelson Mandela", "Complex web scrapers and sub-second voice agents seem daunting until the first successful API call.")
]

def perform_bulletproof_web_search(query: str, limit: int = 3) -> list:
    """Extracts clean real-time search results (titles, snippets, direct URLs)."""
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

def generate_intelligent_answer(query: str, search_results: list, user_name: str) -> str:
    """
    Generates a natural, intelligent human-like answer FIRST,
    incorporating extracted web insights into direct prose.
    """
    q_lower = query.lower()

    # Check for greeting intention
    if any(kw in q_lower for kw in ["greet", "say hi", "welcome everyone", "hello everyone", "good morning", "good afternoon"]):
        return (
            f"Hey everyone in Project Snorlax! 🌸✨ Wishing a fantastic, high-productivity day to our Founder **Vishwajith** (@Vish7781), "
            f"Tech Director **Monkey D Luffy** (@lo_uffy_1999), **Dxrk sky**, and the entire team! ☕⚡ "
            f"Let's make incredible progress on our AI Automations today—Snorlax is here 24/7 to support and power all your work! 😴🔮"
        )

    # Synthesize answer from top web snippets if available
    if search_results:
        best = search_results[0]
        answer_body = f"Here is the breakdown for **{user_name}**:\n\n{best['snippet']}\n\n"
        if len(search_results) > 1:
            answer_body += f"Additionally, key insights show that: {search_results[1]['snippet']}\n\n"
        return answer_body
    else:
        return f"Hey {user_name}! 🌸 Regarding `{query}`, Snorlax processed your request for Project Snorlax AI Automations stack. I am active 24/7 to help you with web research, Notion task updates, and technical workflows! ⚡✨"

def log_team_chat_message(author: str, content: str, channel: str):
    """Passively logs every team message to track workflow state for Telegram reporting."""
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

def generate_telegram_workflow_report() -> str:
    """Generates a detailed personal workflow report of team interactions for Dxrk sky on Telegram."""
    if not os.path.exists(CHAT_LOG_FILE):
        return "📊 **Personal Workflow Report for Dxrk sky:**\nNo team chat activity logged yet today."

    try:
        with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
            chats = json.load(f)
    except Exception:
        chats = []

    total_msgs = len(chats)
    authors = set(c["author"] for c in chats)

    report = (
        f"📊 **PERSONAL TELEGRAM WORKFLOW REPORT (Dxrk sky)** 📊\n"
        f"• **Generated At:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"• **Total Messages Monitored:** {total_msgs}\n"
        f"• **Active Team Members:** {', '.join(authors) if authors else 'None'}\n\n"
        f"🔍 **Workflow State Analysis:**\n"
    )
    for c in chats[-10:]:
        report += f"  • `[{c['author']}]`: {c['content'][:120]}\n"

    report += f"\n⚡ **System Status:** Snorlax 24/7 Autonomous Daemon Active & Self-Healing."
    
    with open(TELEGRAM_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    return report

@bot.event
async def on_ready():
    logging.info(f"⚡ [Snorlax Bot Online] Authenticated as {bot.user} (ID: {bot.user.id})")
    print(f"✅ Snorlax Autonomous Bot Online 24/7! Natural Conversational Responder Active.")
    await bot.change_presence(activity=discord.Game(name="24/7 Conversational AI & Web Research"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Passively log all team messages
    content_raw = message.content.strip()
    if content_raw:
        log_team_chat_message(author=message.author, content=content_raw, channel=str(message.channel))

    # Respond ONLY when explicitly @mentioned or prefixed
    is_mentioned = bot.user.mentioned_in(message)
    is_prefixed = message.content.startswith("!snorlax") or message.content.startswith("!anya") or message.content.startswith("!hermes")

    if is_mentioned or is_prefixed:
        content_clean = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if content_clean.startswith("!snorlax") or content_clean.startswith("!anya") or content_clean.startswith("!hermes"):
            content_clean = content_clean.split(" ", 1)[1] if " " in content_clean else ""

        query_clean = content_clean.strip()
        user_display = message.author.display_name

        # Case 1: Simple Greetings (e.g. "hii", "hello", "hey", "sup", "good morning")
        if query_clean.lower() in ["hii", "hi", "hello", "hey", "sup", "yo", "good morning", "good afternoon"]:
            greeting_msg = random.choice(GREETING_RESPONSES).format(user=message.author.mention)
            await message.channel.send(greeting_msg)
            return

        # Case 2: Status Command
        elif query_clean.lower() == "status":
            embed = discord.Embed(
                title=f"{random.choice(CUTE_EMOJIS)} Snorlax System Status",
                description="**Status:** 100% Operational (24/7)\n**Natural Conversational Engine:** ACTIVE\n**Answer-First + Sources Flow:** ENABLED\n**Telegram Personal Report:** ENABLED",
                color=0x2563eb
            )
            await message.channel.send(embed=embed)
            return

        # Case 3: Questions / Requests / Searches (ANSWER FIRST, REFERENCE WEBPAGES LATER)
        else:
            async with message.channel.typing():
                web_results = perform_bulletproof_web_search(query_clean, limit=3)
                answer_text = generate_intelligent_answer(query_clean, web_results, user_display)

            # Build Natural Human-Like Embed Response
            cute_icon = random.choice(CUTE_EMOJIS)
            embed = discord.Embed(
                title=f"{cute_icon} {user_display}'s Query Answer",
                description=f"Hey **{message.author.mention}** {cute_icon}!\n\n{answer_text}",
                color=0x10b981
            )

            # APPEND SUPPORTED REFERENCE WEBPAGES LATER AT THE BOTTOM
            if web_results:
                sources_text = ""
                for idx, res in enumerate(web_results, 1):
                    sources_text += f"{idx}. **[{res['title'][:80]}]({res['link']})**\n_{res['snippet'][:120]}_\n\n"
                
                embed.add_field(
                    name="🔗 Supporting Web References & Sources",
                    value=sources_text[:1000],
                    inline=False
                )

            embed.set_footer(text=f"Project Snorlax • Always Here 24/7 {random.choice(CUTE_EMOJIS)}")
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found.")
        sys.exit(1)
    
    print("Starting 24/7 Snorlax Bot with Answer-First + Supporting Webpages Engine...")
    bot.run(BOT_TOKEN)
