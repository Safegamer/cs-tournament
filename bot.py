import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# 🔐 SAFE TOKEN (from environment)
TOKEN = os.getenv("TOKEN")

# 📢 YOUR CHANNEL ID
CHANNEL_ID = 1506327211148578886

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"
MSG_FILE = "message_id.txt"

# =====================
# LOAD / SAVE DATA
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"teams": {}, "matches": [], "fixtures": []}
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load()

# =====================
# MESSAGE ID HANDLING (FIXED)
# =====================
def load_msg():
    if not os.path.exists(MSG_FILE):
        return None

    content = open(MSG_FILE).read().strip()
    if content == "":
        return None

    return int(content)

def save_msg(mid):
    with open(MSG_FILE, "w") as f:
        f.write(str(mid))

# =====================
# EMBED LEADERBOARD
# =====================
def create_embed():
    teams = data["teams"]

    sorted_teams = sorted(
        teams.items(),
        key=lambda x: (x[1]["P"], x[1]["W"]),
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 CS Tournament Leaderboard",
        color=0x00ff00
    )

    if not sorted_teams:
        embed.description = "No teams yet"
        return embed

    for i, (team, d) in enumerate(sorted_teams, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."

        embed.add_field(
            name=f"{medal} {team}",
            value=f"Pts:{d['P']} | W:{d['W']} L:{d['L']} M:{d['M']}",
            inline=False
        )

    return embed

# =====================
# UPDATE LEADERBOARD
# =====================
async def update_board():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Channel not found")
        return

    embed = create_embed()
    mid = load_msg()

    try:
        if mid:
            msg = await channel.fetch_message(mid)
            await msg.edit(embed=embed)
        else:
            msg = await channel.send(embed=embed)
            save_msg(msg.id)
    except:
        msg = await channel.send(embed=embed)
        save_msg(msg.id)

# =====================
# BOT READY
# =====================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot Ready as {bot.user}")
    await update_board()

# =====================
# ADD TEAM
# =====================
@bot.tree.command(name="addteam")
async def addteam(interaction: discord.Interaction, name: str):

    if name in data["teams"]:
        return await interaction.response.send_message("❌ Team already exists")

    data["teams"][name] = {"M":0,"W":0,"L":0,"D":0,"P":0}
    save(data)

    await update_board()
    await interaction.response.send_message(f"✅ {name} added")

# =====================
# RESULT + STATS
# =====================
@bot.tree.command(name="result")
async def result(
    interaction: discord.Interaction,
    team1: str,
    team2: str,
    winner: str,
    mvp: str,
    kills: int
):

    if team1 not in data["teams"] or team2 not in data["teams"]:
        return await interaction.response.send_message("❌ Team not found")

    t1 = data["teams"][team1]
    t2 = data["teams"][team2]

    t1["M"] += 1
    t2["M"] += 1

    if winner == team1:
        t1["W"] += 1
        t1["P"] += 2
        t2["L"] += 1
    elif winner == team2:
        t2["W"] += 1
        t2["P"] += 2
        t1["L"] += 1
    else:
        return await interaction.response.send_message("❌ Invalid winner")

    # Save match history
    data["matches"].append({
        "team1": team1,
        "team2": team2,
        "winner": winner,
        "mvp": mvp,
        "kills": kills
    })

    save(data)
    await update_board()

    await interaction.response.send_message("✅ Result + stats saved")

# =====================
# MATCH HISTORY
# =====================
@bot.tree.command(name="history")
async def history(interaction: discord.Interaction):

    if not data["matches"]:
        return await interaction.response.send_message("No matches yet")

    msg = "📜 Match History:\n\n"

    for m in data["matches"][-10:]:
        msg += f"{m['team1']} vs {m['team2']} → {m['winner']} | MVP: {m['mvp']} ({m['kills']} kills)\n"

    await interaction.response.send_message(msg)

# =====================
bot.run(TOKEN)
