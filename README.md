
# Shoutcast Radio Discord Bot

A simple Discord bot for Defiant Network's Shoutcast radio.  
Features:
- Show now playing info
- Auto-post when songs change
- Updates bot status with the current song

## Setup
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```
2. Create `.env` file with your bot token:
```
DISCORD_TOKEN=your_discord_bot_token_here
```
3. Make sure your Discord server has a channel called `radio-updates`.

4. Run the bot:
```bash
python radio_bot.py
```

Enjoy!
