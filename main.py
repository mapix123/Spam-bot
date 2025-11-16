# bot.py — Safe 0.5-second interval spam-like bot (Discord legal)
import discord
import asyncio
import json
import os
from discord.ext import commands

CONFIG_PATH = "config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

async def safe_send(channel, message):
    try:
        await channel.send(message)
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print("Rate limited — backing off...")
            await asyncio.sleep(1)
        else:
            print("HTTP error:", e)

async def spam_loop(bot):
    while True:
        cfg = load_config()
        channel_id = cfg.get("channel_id")
        message = cfg.get("message", "Hello!")
        interval = cfg.get("interval", 0.5)

        if not channel_id:
            print("No channel_id in config.json")
            await asyncio.sleep(1)
            continue

        channel = bot.get_channel(int(channel_id))
        if channel is None:
            try:
                channel = await bot.fetch_channel(int(channel_id))
            except:
                print("Cannot access channel yet.")
                await asyncio.sleep(1)
                continue

        await safe_send(channel, message)
        await asyncio.sleep(interval)

def main():
    cfg = load_config()
    token = os.getenv("DISCORD_BOT_TOKEN") or cfg.get("bot_token")
    prefix = cfg.get("prefix", "!")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=prefix, intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot online as {bot.user}")
        bot.loop.create_task(spam_loop(bot))

    bot.run(token)

if __name__ == "__main__":
    main()
