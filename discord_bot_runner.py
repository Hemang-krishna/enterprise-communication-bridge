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

MOTIVATIONAL_QUOTES = [
    ("“Simplicity is prerequisite for reliability.” — Edsger W. Dijkstra", "Break complex automation nodes into small, focused sub-systems to eliminate mental clutter."),
    ("“The best way to predict the future is to invent it.” — Alan Kay", "Every AI flow you build today shapes the autonomous infrastructure of tomorrow."),
    ("“Action is the foundational key to all success.” — Pablo Picasso", "Start with a working prototype, then iterate rapidly. Perfect execution beats overthinking."),
    ("“It always seems impossible until it's done.” — Nelson Mandela", "Complex web scrapers and sub-second voice agents seem daunting until the first successful API call.")
]

def perform_bulletproof_web_search(query: str, limit: int = 4) -> list:
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
    print(f"✅ Snorlax Autonomous Bot Online 24/7! Monitoring team chats passively & responding on @mentions only.")
    await bot.change_presence(activity=discord.Game(name="24/7 Passive Chat Monitoring & Support"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # PASSIVELY READ AND UNDERSTAND EVERY TEAM MESSAGE (Zero Spam)
    content_raw = message.content.strip()
    if content_raw:
        log_team_chat_message(author=message.author, content=content_raw, channel=str(message.channel))

    # RESPOND IN DISCORD ONLY WHEN EXPLICITLY MENTIONED OR PREFIXED
    is_mentioned = bot.user.mentioned_in(message)
    is_prefixed = message.content.startswith("!snorlax") or message.content.startswith("!anya") or message.content.startswith("!hermes")

    if is_mentioned or is_prefixed:
        content_clean = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if content_clean.startswith("!snorlax") or content_clean.startswith("!anya") or content_clean.startswith("!hermes"):
            content_clean = content_clean.split(" ", 1)[1] if " " in content_clean else ""

        query_clean = content_clean.strip()
        cute_prefix = f"{random.choice(CUTE_EMOJIS)} {random.choice(CUTE_EMOJIS)}"

        if not query_clean:
            query_clean = "AI Automations Project Snorlax"

        # Command: Status
        if query_clean.lower() == "status":
            embed = discord.Embed(
                title=f"{cute_prefix} Snorlax System Status",
                description="**Status:** 100% Operational (24/7)\n**Passive Monitor:** ACTIVE (Reading all team messages)\n**Mention Responder:** ACTIVE (Cute Emojis Only on @mentions)\n**Telegram Personal Report:** ENABLED",
                color=0x2563eb
            )
            await message.channel.send(embed=embed)

        # Command: Team
        elif query_clean.lower() == "team":
            embed = discord.Embed(
                title=f"{cute_prefix} Project Snorlax Team Directory",
                description="**Founder & Supreme Lead:** Vishwajith (@Vish7781)\n**Director in Technology:** Monkey D Luffy (@lo_uffy_1999)\n**Workspace Owner:** Dxrk sky\n**AI Operating Agent:** Snorlax / Hermes",
                color=0x8b5cf6
            )
            await message.channel.send(embed=embed)

        # UNIVERSAL CUTE RESPONDER ON @MENTIONS
        else:
            search_term = re.sub(r'^(search|research|find|look up)\s+', '', query_clean, flags=re.IGNORECASE).strip()
            
            async with message.channel.typing():
                web_results = perform_bulletproof_web_search(search_term)

            if web_results:
                embed = discord.Embed(
                    title=f"{cute_prefix} Snorlax Answer for {message.author.display_name}",
                    description=f"Hello **{message.author.mention}** {random.choice(CUTE_EMOJIS)}! Here are real-time web insights for your question:\n\n💬 `{query_clean}`",
                    color=0x10b981
                )
                for res in web_results[:3]:
                    embed.add_field(
                        name=f"🌐 {res['title'][:200]}",
                        value=f"{res['snippet'][:250]}\n🔗 **[Read Source Link]({res['link']})**",
                        inline=False
                    )
                embed.set_footer(text=f"Project Snorlax • Always Available 24/7 {random.choice(CUTE_EMOJIS)}")
                await message.channel.send(embed=embed)
            else:
                quote, tip = random.choice(MOTIVATIONAL_QUOTES)
                embed = discord.Embed(
                    title=f"{cute_prefix} Snorlax Answer for {message.author.display_name}",
                    description=f"Hello **{message.author.mention}** {random.choice(CUTE_EMOJIS)}!\n\n💬 `{query_clean}`\n\n💡 **Tip:** {tip}\n📜 **Quote:** {quote}",
                    color=0x3b82f6
                )
                embed.set_footer(text=f"Project Snorlax • Always Available 24/7 {random.choice(CUTE_EMOJIS)}")
                await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found.")
        sys.exit(1)
    
    print("Starting 24/7 Snorlax Bot with Passive Chat Reading & @Mention Only Responding...")
    bot.run(BOT_TOKEN)
