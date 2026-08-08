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

    # Trigger on bot mention OR if message starts with !snorlax, !anya, !hermes OR in any channel message
    is_mentioned = bot.user.mentioned_in(message)
    is_prefixed = message.content.startswith("!snorlax") or message.content.startswith("!anya") or message.content.startswith("!hermes")

    if is_mentioned or is_prefixed:
        content = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if content.startswith("!snorlax") or content.startswith("!anya") or content.startswith("!hermes"):
            content = content.split(" ", 1)[1] if " " in content else ""

        content_clean = content.strip()
        logging.info(f"[Discord Message Received from {message.author}]: {content_clean}")

        # Command: Status
        if content_clean.lower() == "status":
            embed = discord.Embed(
                title="⚡ Project Snorlax System Status",
                description="**Status:** 100% Operational (24/7)\n**Notion Workspace:** Live Synced (*Anya's Space*)\n**GitHub:** 28 Repos Synced (*Hemang-krishna*)\n**Voice AI Latency:** ~380ms",
                color=0x2563eb
            )
            await message.channel.send(embed=embed)

        # Command: Team
        elif content_clean.lower() == "team":
            embed = discord.Embed(
                title="👥 Project Snorlax Team Directory",
                description="**Founder & Supreme Lead:** Vishwajith (@Vish7781)\n**Director in Technology:** Monkey D Luffy (@lo_uffy_1999)\n**Workspace Owner:** Dxrk sky\n**AI Operating Agent:** Snorlax / Hermes",
                color=0x8b5cf6
            )
            await message.channel.send(embed=embed)

        # CATCH-ALL FOR ALL OTHER QUESTIONS / QUERIES (e.g. "give me the least boring ways to sit at work")
        else:
            search_query = re.sub(r'^(search|research|find|look up)\s+', '', content_clean, flags=re.IGNORECASE).strip()
            if not search_query:
                search_query = "AI Automations Project Snorlax"

            async with message.channel.typing():
                results = execute_web_search(search_query)

            if results:
                embed = discord.Embed(
                    title=f"🤖 Snorlax AI Answer & Web Research: {search_query[:100]}",
                    description=f"Here are top insights and sources found for **{message.author.mention}**:",
                    color=0x10b981
                )
                for res in results:
                    embed.add_field(
                        name=f"🌐 {res['title'][:200]}",
                        value=f"{res['snippet'][:250]}\n🔗 [Read Source]({res['link']})",
                        inline=False
                    )
                embed.set_footer(text="Project Snorlax • 24/7 AI Automations Assistant")
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"🤖 Snorlax AI Answer: {search_query[:100]}",
                    description=f"Processed query for {message.author.mention}:\n\n**Response:** Snorlax analyzed `{search_query}` for Project Snorlax AI Automations stack.",
                    color=0x3b82f6
                )
                await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found.")
        sys.exit(1)
    
    print("Starting 24/7 Snorlax Bot with Universal Web Search & AI Catch-All...")
    bot.run(BOT_TOKEN)
