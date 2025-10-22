from datetime import datetime
from discord.ext import commands
import discord
import io, os, shutil
from PIL import Image
import requests
import aiohttp
import os
import subprocess

BASE_PATH = os.path.join(os.getcwd(), "requests")
REPO_PATH = os.getcwd()
PENDING_PATH = os.path.join(BASE_PATH, "pending")
ACCEPTED_PATH = os.path.join(BASE_PATH, "accepted")
os.makedirs(PENDING_PATH, exist_ok=True)
os.makedirs(ACCEPTED_PATH, exist_ok=True)

TOKEN = os.environ.get("DISCORD_TOKEN")
REVIEW_CHANNEL_ID = int(os.environ.get("REVIEW_CHANNEL_ID", "1429486591440588993"))
RESULT_CHANNEL_ID = int(os.environ.get("RESULT_CHANNEL_ID", "1429744076714016829"))

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.review_messages = {}

@bot.event
async def on_ready():
    print(f"Connected as {bot.user}")

def git_sync(commit_msg="auto sync"):
    try:
        subprocess.run(["git", "-C", REPO_PATH, "add", "."], check=True)
        subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "-C", REPO_PATH, "push"], check=True)
        print("✅ Git synchronized.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erreur Git : {e}")

@bot.command()
async def balls(ctx):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{timestamp}_{ctx.author.name}_ballfight"
    folder_path = os.path.join(PENDING_PATH, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    with open(os.path.join(folder_path, "info.txt"), "w", encoding="utf-8") as f:
        f.write(f"Command used by {ctx.author} at {timestamp}\n")

    mentions = ctx.message.mentions
    if not mentions or len(mentions) == 1:
        await ctx.send("⚠️ You need to mention at least two users!")
        return

    await ctx.send(f"⏳ Creating request: `{folder_name}`\n📸 downloading {len(mentions)} avatars...")

    files = []
    for i, member in enumerate(mentions, start=1):
        try:
            avatar_asset = member.avatar
            avatar_bytes = await avatar_asset.read()
            img = Image.open(io.BytesIO(avatar_bytes))

            avatar_path = os.path.join(folder_path, f"avatar_{i}_{member.name}.png")
            img.save(avatar_path, format="PNG")

            files.append(discord.File(avatar_path, filename=f"profil_{i}.png"))
        except Exception as e:
            print(f"Error with user {member}: {e}")

    review_channel = bot.get_channel(REVIEW_CHANNEL_ID)
    embed = discord.Embed(
        title="New ballfight request",
        description=f"Requested by {ctx.author.mention}\nMentions: {', '.join(m.mention for m in mentions)}"
    )

    if files:
        embed.set_image(url="attachment://profil_1.png")

    review_message = await review_channel.send(
        content=f"🎬 New request from {ctx.author.mention}! Need to be verified",
        files=files,
        embed=embed
    )

    await review_message.add_reaction("✅")
    await review_message.add_reaction("❌")

    await ctx.send(f"✅ {len(files)} sent for review :D")

    bot.review_messages[review_message.id] = {
        "author": ctx.author,
        "mentions": mentions,
        "folder": folder_path,
        "name": folder_name
    }

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message = reaction.message
    if message.id not in bot.review_messages:
        return

    info = bot.review_messages[message.id]
    folder_path = info["folder"]
    folder_name = info["name"]
    author = info["author"]
    mentions = info["mentions"]

    if reaction.emoji == "✅":
        dest_path = os.path.join(ACCEPTED_PATH, folder_name)
        try:
            shutil.move(folder_path, dest_path)
            await message.channel.send(
                f"✅ Request from {author.mention} approved by {user.mention}! Moving to accepted requests..."
            )
            result_channel = bot.get_channel(RESULT_CHANNEL_ID)
            embed = discord.Embed(
                title="Ballfight Request Accepted",
                description=f"{author.mention}, your request has been accepted!\nParticipating: {', '.join(m.mention for m in mentions)}\n,Your video will be created soon!"
            )
            await result_channel.send(embed=embed)
            
            git_sync(commit_msg=f"Auto commit: création {folder_name}")
            
        except Exception as e:
            await message.channel.send(f"⚠️ Error while moving: `{e}`")
        

    elif reaction.emoji == "❌":
        try:
            shutil.rmtree(folder_path)
            await message.channel.send(
                f"❌ Request from {author.mention} denied by {user.mention}. Deleting request..."
            )
        except Exception as e:
            await message.channel.send(f"⚠️ Error while deleting: `{e}`")

    del bot.review_messages[message.id]

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN environment variable is not set!")
        print("Please set the DISCORD_TOKEN secret in your Replit environment.")
        exit(1)
    
    bot.run(TOKEN)