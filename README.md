# 🎧 Defiance Radio Discord Bot

A custom Discord bot that streams your Shoutcast radio station with commands to control playback, stream quality, and show listener stats — all from Discord.

## 🚀 Features

- `/cmds` — List all available commands
- `/join` — Join a voice channel
- `/leave` — Leave the voice channel
- `/play` — Start streaming the radio
- `/quality [kbps]` — Change stream bitrate
- `/whatsplaying` — Show the currently playing track
- `/statusinterval [seconds]` — Change how often status updates
- `/openstream` — Share direct stream link
- `/website` — Share your station’s website
- `/streaminfo` — Show real-time bitrate, uptime, and listener count

## ⚙️ Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and fill in your bot token, guild ID, and stream URLs
4. Run the bot:
   ```bash
   python bot.py
   ```

## 🛠 Requirements

- Python 3.10+
- A working Shoutcast stream with JSON stats available at `/stats?json=1`

---

🎉 Powered by [Defiance Radio](http://www.defiantnetwork.co.uk) – where the party’s never stop!
