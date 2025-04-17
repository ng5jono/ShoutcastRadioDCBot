
import discord
from discord.ext import tasks
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SHOUTCAST_URL = 'http://defiantnetwork.co.uk:4445/stats?sid=1&json=1'

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

last_song = None

def fetch_shoutcast_info():
    try:
        response = requests.get(SHOUTCAST_URL, timeout=5)
        data = response.json()
        song = data.get('songtitle', 'No song info')
        listeners = data.get('currentlisteners', 'Unknown')
        dj = data.get('servicenick', 'DJ not available')
        return song, listeners, dj
    except Exception as e:
        return f"Error: {e}", "Unknown", "Unknown"

@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user}')
    check_for_new_song.start()

@tree.command(name="nowplaying", description="Show the current song, listener count, and DJ")
async def nowplaying(interaction: discord.Interaction):
    song, listeners, dj = fetch_shoutcast_info()
    await interaction.response.send_message(f"**Now Playing:** {song}\n**Listeners:** {listeners}\n**DJ:** {dj}", ephemeral=False)

@tree.command(name="listeners", description="Show how many listeners are tuned in")
async def listeners(interaction: discord.Interaction):
    _, listeners, _ = fetch_shoutcast_info()
    await interaction.response.send_message(f"👥 **Current Listeners:** {listeners}", ephemeral=False)

@tree.command(name="dj", description="Show the current DJ's name")
async def dj(interaction: discord.Interaction):
    _, _, dj_name = fetch_shoutcast_info()
    await interaction.response.send_message(f"🎧 **Current DJ:** {dj_name}", ephemeral=False)

@tree.command(name="help", description="List all available radio bot commands")
async def help_command(interaction: discord.Interaction):
    help_text = (
        "**Radio Bot Commands:**\n"
        "/nowplaying — Show the current song, listener count, and DJ\n"
        "/listeners — Show the number of listeners\n"
        "/dj — Show the current DJ\n"
        "/help — Show this help message"
    )
    await interaction.response.send_message(help_text, ephemeral=True)

@tasks.loop(seconds=30)
async def check_for_new_song():
    global last_song
    song, listeners, dj = fetch_shoutcast_info()
    if song != last_song:
        last_song = song
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name='radio-updates')
            if channel:
                await channel.send(f"**Now Playing:** {song}\n**Listeners:** {listeners}\n**DJ:** {dj}")
        await bot.change_presence(activity=discord.Game(name=f"🎵 {song}"))

bot.run(TOKEN)
