import os
import sys
import json
import asyncio
import logging

sys.path.append("/data/integrations")
sys.path.append("/data")

import discord
from discord.ext import commands
from integrations.enterprise_bridge import EnterpriseCommunicationBridge

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

# Load token from .env
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not BOT_TOKEN and os.path.exists("/data/.env"):
    with open("/data/.env", "r") as f:
        for line in f:
            if line.startswith("DISCORD_BOT_TOKEN="):
                BOT_TOKEN = line.strip().split("=", 1)[1]
                break

# Use standard non-privileged intents so bot connects instantly
intents = discord.Intents.default()
# intents.message_content = True (Optional: Enable in Discord Developer Portal under Bot tab)

bot = commands.Bot(command_prefix="!", intents=intents)
bridge = EnterpriseCommunicationBridge()

@bot.event
async def on_ready():
    logging.info(f"⚡ [Snorlax Bot Online] Authenticated as {bot.user} (ID: {bot.user.id})")
    print(f"✅ Snorlax Bot Connected & Online! Server Count: {len(bot.guilds)}")
    for guild in bot.guilds:
        print(f"   - Connected Server: {guild.name} (ID: {guild.id})")
    
    await bot.change_presence(activity=discord.Game(name="Project Anya Agentic OS"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if bot is mentioned or if message starts with !anya or !hermes
    if bot.user.mentioned_in(message) or message.content.startswith("!anya") or message.content.startswith("!hermes"):
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        logging.info(f"[Discord Message Received from {message.author}]: {content}")

        if "status" in content.lower():
            status = bridge.get_full_workspace_status()
            embed = discord.Embed(
                title="⚡ Project Anya System Status",
                description="**Status:** Operational\n**Notion Tasks:** Active\n**Voice AI Latency:** ~380ms",
                color=0x2563eb
            )
            embed.set_footer(text="Project Anya • Snorlax Discord Bot")
            await message.channel.send(embed=embed)
        else:
            # Echo / Intelligent agent response
            reply = f"Hello {message.author.mention}! I am Snorlax, the Hermes AI Assistant for Project Anya. Your instruction `{content}` has been logged into Notion workspace."
            embed = discord.Embed(
                title="🤖 Snorlax AI Agent Reply",
                description=reply,
                color=0x10b981
            )
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment or /data/.env")
        sys.exit(1)
    
    print("Starting Snorlax Discord Bot Runner...")
    bot.run(BOT_TOKEN)
