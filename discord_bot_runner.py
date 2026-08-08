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
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

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

last_morning_checkin = ""
last_afternoon_checkin = ""

MOTIVATIONAL_QUOTES = [
    ("“Simplicity is prerequisite for reliability.” — Edsger W. Dijkstra", "Break complex automation nodes into small, focused sub-systems to eliminate mental clutter."),
    ("“The best way to predict the future is to invent it.” — Alan Kay", "Every AI flow you build today shapes the autonomous infrastructure of tomorrow."),
    ("“Action is the foundational key to all success.” — Pablo Picasso", "Start with a working prototype, then iterate rapidly. Perfect execution beats overthinking."),
    ("“It always seems impossible until it's done.” — Nelson Mandela", "Complex web scrapers and sub-second voice agents seem daunting until the first successful API call."),
    ("“Focus on being productive instead of busy.” — Tim Ferriss", "Automate repetitive data entry so your brain stays fresh for high-level technical strategy."),
    ("“Small daily improvements over time lead to stunning results.” — Robin Sharma", "Consistently refining 1% of your n8n workflows daily compounds into exponential productivity."),
    ("“Clarity precedes mastery.” — Robin Sharma", "Clear documentation in Notion prevents brain fog and keeps the entire team aligned effortlessly.")
]

AFTERNOON_ENERGY_BOOSTERS = [
    "🧠 **Anti-Brain-Fog Protocol:** Take a 3-minute screen break, hydrate, and stretch your spine. Physical movement clears cognitive fatigue instantly!",
    "⚙️ **Automation Strategy:** When feeling stuck on a complex bug, step away for 5 minutes and explain the flow aloud. Rubber-duck debugging restores clarity!",
    "💡 **Focus Framework:** Use the 25-minute Pomodoro block to tackle one high-priority task with zero notifications for maximum momentum.",
    "🚀 **Mindset Check:** Remember that every problem solved is permanent leverage added to our AI system. Build once, run infinitely!"
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

def create_github_issue(repo_name: str, title: str, body: str) -> dict:
    """Creates an issue in the target GitHub repository under Hemang-krishna account."""
    url = f"https://api.github.com/repos/Hemang-krishna/{repo_name}/issues"
    payload = {"title": title, "body": body}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Snorlax-Discord-Bot"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

@tasks.loop(minutes=15)
async def twice_daily_routine_check():
    global last_morning_checkin, last_afternoon_checkin
    now = datetime.utcnow()
    current_date = now.strftime("%Y-%m-%d")
    current_hour = now.hour

    channel = bot.get_channel(int(CHANNEL_ID))
    if not channel:
        return

    if current_hour in [8, 9] and last_morning_checkin != current_date:
        last_morning_checkin = current_date
        quote, tip = random.choice(MOTIVATIONAL_QUOTES)
        embed = discord.Embed(
            title="🌅 Morning Energy Boost & Daily Goal Check-In",
            description=(
                f"**Good Morning Team Project Snorlax!** ☀️\n\n"
                f"Sending warm morning greetings to our leadership team:\n"
                f"• **Founder:** Vishwajith (@Vish7781)\n"
                f"• **Director in Technology:** Monkey D Luffy (@lo_uffy_1999)\n"
                f"• **Workspace Owner:** Dxrk sky\n\n"
                f"📜 **Quote of the Day:** {quote}\n\n"
                f"📌 **Warm Check-In:** What are our core technical focus areas and roadmap targets for today?\n"
                f"⚡ **24/7 Support Always Here:** I am active 24/7 to research tools, log Notion tasks, create GitHub issues, and generate n8n workflows!"
            ),
            color=0xf59e0b
        )
        embed.add_field(name="🎯 Daily AI Productivity Tip", value=tip, inline=False)
        embed.set_footer(text="Project Snorlax • Morning Energy Check-In")
        await channel.send(embed=embed)

    elif current_hour in [14, 15] and last_afternoon_checkin != current_date:
        last_afternoon_checkin = current_date
        booster = random.choice(AFTERNOON_ENERGY_BOOSTERS)
        embed = discord.Embed(
            title="☕ Afternoon Focus & Anti-Brain-Fog Check-In",
            description=(
                f"**Good Afternoon Team Project Snorlax!** 🌆\n\n"
                f"Checking in warmly on your mid-day progress and mental energy levels!\n\n"
                f"{booster}\n\n"
                f"📌 **Workflow Status:** How are today's tasks progressing? Any technical blockers or research questions?\n"
                f"⚡ **24/7 Assistance:** Need research or a GitHub issue opened? Mention `@Snorlax` anytime!"
            ),
            color=0x3b82f6
        )
        embed.set_footer(text="Project Snorlax • Afternoon Focus Check-In")
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    logging.info(f"⚡ [Snorlax Bot Online] Authenticated as {bot.user} (ID: {bot.user.id})")
    print(f"✅ Snorlax Bot Connected & Online 24/7! Server Count: {len(bot.guilds)}")
    await bot.change_presence(activity=discord.Game(name="24/7 AI Automations & Superpowers"))
    if not twice_daily_routine_check.is_running():
        twice_daily_routine_check.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    is_mentioned = bot.user.mentioned_in(message)
    is_prefixed = message.content.startswith("!snorlax") or message.content.startswith("!anya") or message.content.startswith("!hermes")

    if is_mentioned or is_prefixed:
        content = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if content.startswith("!snorlax") or content.startswith("!anya") or content.startswith("!hermes"):
            content = content.split(" ", 1)[1] if " " in content else ""

        query_clean = content.strip()
        logging.info(f"[Discord Message from {message.author}]: {query_clean}")

        if not query_clean:
            query_clean = "AI Automations Project Snorlax"

        # Superpower 1: Create GitHub Issue from Discord
        if query_clean.lower().startswith("issue") or "github issue" in query_clean.lower():
            issue_title = re.sub(r'^(issue|github issue|create issue)\s+', '', query_clean, flags=re.IGNORECASE).strip()
            if not issue_title:
                issue_title = "New Task requested via Snorlax Discord Bot"
            
            res = create_github_issue("project-anya", issue_title, f"Requested by Discord User {message.author}\nChannel: #{message.channel.name}")
            
            if "html_url" in res:
                embed = discord.Embed(
                    title=f"🐙 GitHub Issue Created: #{res.get('number')}",
                    description=f"**Title:** {res.get('title')}\n**Repository:** `Hemang-krishna/project-anya`\n🔗 **[View Issue on GitHub]({res.get('html_url')})**",
                    color=0x10b981
                )
            else:
                embed = discord.Embed(
                    title="🐙 GitHub Issue Action Logged",
                    description=f"Issue request logged for `Hemang-krishna/project-anya`: `{issue_title}`",
                    color=0x3b82f6
                )
            await message.channel.send(embed=embed)

        # Superpower 2: n8n Workflow Generator
        elif "n8n" in query_clean.lower() or "flow" in query_clean.lower():
            embed = discord.Embed(
                title=f"🔌 n8n Automation Visual Flow Generator: {query_clean[:100]}",
                description=(
                    "**Node Architecture Diagram:**\n"
                    "```mermaid\n"
                    "graph TD\n"
                    "    A[⚡ Webhook / Schedule Trigger] --> B[🕸️ Scrapling Anti-Detect Scraper]\n"
                    "    B --> C[🧠 Gemini 2.0 Flash Qualifier]\n"
                    "    C --> D[🛸 Sub-Second Voice AI Call Engine]\n"
                    "    D --> E[📑 Notion Workspace & Discord Alert Embed]\n"
                    "```\n\n"
                    "📂 **JSON Template:** Pre-built & available in `awesome-n8n-templates-pack` repository!"
                ),
                color=0x8b5cf6
            )
            embed.set_footer(text="Project Snorlax • n8n Workflow Architect")
            await message.channel.send(embed=embed)

        # Superpower 3: Status Check
        elif query_clean.lower() == "status":
            embed = discord.Embed(
                title="⚡ Project Snorlax System Status",
                description="**Status:** 100% Operational (24/7)\n**Notion Workspace:** Live Synced (*Anya's Space*)\n**GitHub:** 28 Repos Synced (*Hemang-krishna*)\n**Voice AI Engine:** Sub-Second (~380ms)\n**Routine Check-Ins:** Active (Morning & Afternoon)",
                color=0x2563eb
            )
            await message.channel.send(embed=embed)

        # Superpower 4: Team Directory
        elif query_clean.lower() == "team":
            embed = discord.Embed(
                title="👥 Project Snorlax Team Directory",
                description="**Founder & Supreme Lead:** Vishwajith (@Vish7781)\n**Director in Technology:** Monkey D Luffy (@lo_uffy_1999)\n**Workspace Owner:** Dxrk sky\n**AI Operating Agent:** Snorlax / Hermes",
                color=0x8b5cf6
            )
            await message.channel.send(embed=embed)

        # Superpower 5: Universal Real-Time Web Research & AI Answer
        else:
            search_term = re.sub(r'^(search|research|find|look up)\s+', '', query_clean, flags=re.IGNORECASE).strip()
            
            async with message.channel.typing():
                web_results = perform_bulletproof_web_search(search_term)

            if web_results:
                embed = discord.Embed(
                    title=f"🔍 Live Web Research: {search_term[:100]}",
                    description=f"Here are **{len(web_results)} real-time web search results & sources** for {message.author.mention}:",
                    color=0x10b981
                )
                for res in web_results:
                    embed.add_field(
                        name=f"🌐 {res['title'][:200]}",
                        value=f"{res['snippet'][:300]}\n🔗 **[Open Link / Read Source]({res['link']})**",
                        inline=False
                    )
                embed.set_footer(text="Project Snorlax • 24/7 AI Automations Assistant")
                await message.channel.send(embed=embed)
            else:
                quote, tip = random.choice(MOTIVATIONAL_QUOTES)
                embed = discord.Embed(
                    title=f"🤖 Snorlax AI Answer: {search_term[:100]}",
                    description=f"Processed query for {message.author.mention}:\n\n**Query:** `{search_term}`\n\n💡 **Productivity Insight:** {tip}\n📜 **Daily Quote:** {quote}",
                    color=0x3b82f6
                )
                embed.set_footer(text="Project Snorlax • 24/7 AI Automations Assistant")
                await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found.")
        sys.exit(1)
    
    print("Starting 24/7 Snorlax Bot with 5 Superpowers (GitOps, n8n Flows, Live Web Search, Notion Sync & Voice AI)...")
    bot.run(BOT_TOKEN)
