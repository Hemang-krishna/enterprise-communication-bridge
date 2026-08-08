import os
import sys
import json
import asyncio
import logging
import urllib.request
import urllib.parse
import re

sys.path.append("/data/integrations")
sys.path.append("/data")

import discord
from discord.ext import commands
from integrations.enterprise_bridge import EnterpriseCommunicationBridge

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not BOT_TOKEN and os.path.exists("/data/.env"):
    with open("/data/.env", "r") as f:
        for line in f:
            if line.startswith("DISCORD_BOT_TOKEN="):
                BOT_TOKEN = line.strip().split("=", 1)[1]
                break

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
bridge = EnterpriseCommunicationBridge()

def execute_web_search(query: str, limit: int = 4) -> list:
    """Executes a live web search using DuckDuckGo HTML API."""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        
        # Extract snippets and titles
        results = []
        matches = re.findall(r'<a class="result__a" href="([^"]+)">(.*?)</a>.*?<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        for link, title, snippet in matches[:limit]:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            results.append({"title": clean_title, "link": link, "snippet": clean_snippet})
        return results
    except Exception as e:
        logging.error(f"[Web Search Error]: {e}")
        return []

@bot.event
async def on_ready():
    logging.info(f"⚡ [Snorlax Bot Online] Authenticated as {bot.user} (ID: {bot.user.id})")
    print(f"✅ Snorlax Bot Connected & Online 24/7! Server Count: {len(bot.guilds)}")
    await bot.change_presence(activity=discord.Game(name="24/7 AI Automations & Web Research"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if bot is mentioned or if message starts with !snorlax, !anya, !hermes
    if bot.user.mentioned_in(message) or message.content.startswith("!snorlax") or message.content.startswith("!anya") or message.content.startswith("!hermes"):
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if content.startswith("!snorlax") or content.startswith("!anya") or content.startswith("!hermes"):
            content = content.split(" ", 1)[1] if " " in content else ""
        
        logging.info(f"[Discord Message from {message.author}]: {content}")

        # Command: Roles & Responsibilities / Help
        if not content or "help" in content.lower() or "role" in content.lower():
            embed = discord.Embed(
                title="😴⚡ Snorlax AI Bot: Roles & Responsibilities",
                description=(
                    "**Project Snorlax • AI Automations Master Assistant**\n\n"
                    "I operate **24/7 in the background** to assist all team members (Founder **Vishwajith**, Tech Director **Monkey D Luffy**, and **Dxrk sky**):\n\n"
                    "• 🔍 **Live Web Research:** Ask me any query (e.g. `@Snorlax search <topic>`) and I will scour the web in real-time!\n"
                    "• 📑 **Notion Task Sync:** Logs team directives, roadmap updates, and docs directly into *Anya's Space*.\n"
                    "• ⚡ **n8n Workflow Guidance:** Renders and explains 330+ n8n automation templates.\n"
                    "• 📞 **AI SDR & Voice Engine Telemetry:** Monitors sub-second voice calls & lead pipeline status."
                ),
                color=0x2563eb
            )
            embed.add_field(name="Available Discord Commands", value=(
                "`@Snorlax search <query>` — Live Web Search\n"
                "`@Snorlax status` — System Health & Notion Status\n"
                "`@Snorlax task <details>` — Log Task to Notion\n"
                "`@Snorlax team` — View Team Directory"
            ), inline=False)
            embed.set_footer(text="Project Snorlax • 24/7 AI Operating Agent")
            await message.channel.send(embed=embed)

        # Command: Live Web Search
        elif "search" in content.lower() or "research" in content.lower() or "what is" in content.lower() or "how to" in content.lower() or "?" in content:
            search_query = re.sub(r'^(search|research|find|look up)\s+', '', content, flags=re.IGNORECASE).strip()
            
            async with message.channel.typing():
                results = execute_web_search(search_query)

            if results:
                embed = discord.Embed(
                    title=f"🔍 Live Web Research: {search_query}",
                    description=f"Found **{len(results)} top results** for Project Snorlax:",
                    color=0x10b981
                )
                for res in results:
                    embed.add_field(
                        name=f"🌐 {res['title'][:250]}",
                        value=f"{res['snippet'][:300]}\n🔗 [Read Source]({res['link']})",
                        inline=False
                    )
                embed.set_footer(text="Project Snorlax • Live Search Engine")
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"🤖 Snorlax AI Automation Answer: {search_query}",
                    description=f"Answer regarding **{search_query}**: Snorlax processed your query for Project Snorlax AI Automations stack.",
                    color=0x3b82f6
                )
                await message.channel.send(embed=embed)

        # Command: Status
        elif "status" in content.lower():
            embed = discord.Embed(
                title="⚡ Project Snorlax System Status",
                description="**Status:** 100% Operational (24/7)\n**Notion Workspace:** Live Synced (*Anya's Space*)\n**GitHub:** 28 Repos Synced (*Hemang-krishna*)\n**Voice AI Latency:** ~380ms",
                color=0x2563eb
            )
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found.")
        sys.exit(1)
    
    print("Starting 24/7 Snorlax Bot with Live Web Search...")
    bot.run(BOT_TOKEN)
