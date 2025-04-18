import os
import asyncio
import discord
import requests
from discord.ext import tasks
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
STREAM_URL = os.getenv("SHOUTCAST_STREAM_URL")
DEFAULT_BITRATE = int(os.getenv("DEFAULT_BITRATE", 128))
STATUS_UPDATE_INTERVAL = int(os.getenv("STATUS_UPDATE_INTERVAL", 30))

intents = discord.Intents.default()
intents.message_content = False
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

voice_client = None
status_task = None
current_title = None


def get_stream_info():
    stats_url = os.getenv("SHOUTCAST_STATS_URL", STREAM_URL.rstrip("/") + "/stats?json=1")
    try:
        response = requests.get(stats_url, timeout=5)
        data = response.json()
        return {
            "current_song": data.get("songtitle"),
            "bitrate": data.get("bitrate"),
            "listeners": data.get("currentlisteners"),
            "max_listeners": data.get("maxlisteners"),
            "uptime": data.get("streamuptime")
        }
    except Exception as e:
        print(f"[Stream Info Error] {e}")
        return None


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f'✅ Logged in as {client.user}')
    update_status.start()


@tree.command(name="cmds", description="List all available commands", guild=discord.Object(id=GUILD_ID))
async def cmds(interaction: discord.Interaction):
    commands_list = '''
📻 **Radio Bot Commands**:

`/cmds` – Show this help message  
`/join` – Join your voice channel  
`/leave` – Leave the voice channel  
`/play` – Start streaming the radio  
`/quality [kbps]` – Set the stream bitrate (e.g. 64, 96, 128)  
`/whatsplaying` – Show what's currently playing in chat  
`/statusinterval [seconds]` – Set how often the bot updates its status (min: 5s)  
`/website` – Opens the Defiant Network website  
`/openstream` – Get a direct link to the live radio stream  
`/streaminfo` – Show live stream info like bitrate, uptime, listeners
'''
    await interaction.response.send_message(commands_list)


@tree.command(name="join", description="Join your voice channel", guild=discord.Object(id=GUILD_ID))
async def join(interaction: discord.Interaction):
    global voice_client
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        voice_client = await channel.connect()
        await interaction.response.send_message("🎶 Joined the voice channel.")
    else:
        await interaction.response.send_message("❌ You must be in a voice channel.")


@tree.command(name="leave", description="Leave the voice channel", guild=discord.Object(id=GUILD_ID))
async def leave(interaction: discord.Interaction):
    global voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None
        await interaction.response.send_message("👋 Left the voice channel.")
        await client.change_presence(status=discord.Status.invisible)
    else:
        await interaction.response.send_message("❌ I'm not in a voice channel.")


@tree.command(name="play", description="Start streaming the radio", guild=discord.Object(id=GUILD_ID))
async def play(interaction: discord.Interaction):
    global voice_client
    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("❌ I'm not connected to a voice channel.")
        return
    try:
        voice_client.stop()
    except:
        pass
    voice_client.play(discord.FFmpegPCMAudio(STREAM_URL, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
    await interaction.response.send_message("▶️ Now streaming Defiance Radio!")


@tree.command(name="quality", description="Set the stream bitrate", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(kbps="Bitrate in kbps (e.g. 64, 96, 128)")
async def quality(interaction: discord.Interaction, kbps: int):
    global STREAM_URL
    if kbps not in [64, 96, 128, 192]:
        await interaction.response.send_message("❌ Please select from 64, 96, 128, or 192 kbps.")
        return
    STREAM_URL = STREAM_URL.rsplit("/", 1)[0] + f"/{kbps}"
    await interaction.response.send_message(f"✅ Stream quality set to {kbps} kbps.")


@tree.command(name="whatsplaying", description="Show what's currently playing", guild=discord.Object(id=GUILD_ID))
async def whatsplaying(interaction: discord.Interaction):
    info = get_stream_info()
    if not info or not info.get("current_song"):
        await interaction.response.send_message("❌ Could not fetch the current song.")
        return
    await interaction.response.send_message(f"🎶 Now Playing: **{info['current_song']}**")


@tree.command(name="statusinterval", description="Set how often the bot updates its status (in seconds)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(seconds="Interval in seconds (min: 5)")
async def statusinterval(interaction: discord.Interaction, seconds: int):
    global STATUS_UPDATE_INTERVAL
    if seconds < 5:
        await interaction.response.send_message("⏱️ Please use at least 5 seconds.", ephemeral=True)
        return
    STATUS_UPDATE_INTERVAL = seconds
    await interaction.response.send_message(f"✅ Status update interval set to {seconds} seconds.")


@tree.command(name="website", description="Open the Defiant Network website", guild=discord.Object(id=GUILD_ID))
async def website(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎧 Tune in to Defiance Radio",
        description="Where the party's never stop! 💃🕺\n\n👉 [Visit defiantnetwork.co.uk](http://www.defiantnetwork.co.uk)",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url="https://www.defiantnetwork.co.uk/logo.png")
    await interaction.response.send_message(embed=embed)


@tree.command(name="openstream", description="Open the live radio stream", guild=discord.Object(id=GUILD_ID))
async def openstream(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔊 Listen Live to Defiance Radio",
        description=f"Click below to open the live stream now!\n\n👉 [Open Stream]({STREAM_URL})",
        color=discord.Color.green()
    )
    embed.set_footer(text="Powered by Defiant Network")
    await interaction.response.send_message(embed=embed)


@tree.command(name="streaminfo", description="View live stream info", guild=discord.Object(id=GUILD_ID))
async def streaminfo(interaction: discord.Interaction):
    info = get_stream_info()
    if not info:
        await interaction.response.send_message("❌ Couldn't fetch stream info right now.")
        return
    embed = discord.Embed(
        title="📡 Defiance Radio Stream Info",
        color=discord.Color.blue()
    )
    embed.add_field(name="🎶 Now Playing", value=info['current_song'] or "N/A", inline=False)
    embed.add_field(name="📶 Bitrate", value=f"{info['bitrate']} kbps", inline=True)
    embed.add_field(name="👥 Listeners", value=f"{info['listeners']} / {info['max_listeners']}", inline=True)
    embed.add_field(name="⏱️ Uptime", value=f"{info['uptime']} mins", inline=True)
    await interaction.response.send_message(embed=embed)


@tasks.loop(seconds=30)
async def update_status():
    global current_title
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            info = get_stream_info()
            if info and info.get("current_song") != current_title:
                current_title = info["current_song"]
                await client.change_presence(activity=discord.Game(name=f"{current_title}"))
        except Exception as e:
            print(f"[Status Update Error] {e}")
        await asyncio.sleep(STATUS_UPDATE_INTERVAL)


client.run(TOKEN)
