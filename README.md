# MusicBot

A Discord music bot that plays audio from YouTube in voice channels.

**No Python installation required.** The `dist/` folder contains a ready-to-use `MusicBot.exe` -- just configure your token and run it.

---

## Quick Start (no programming required)

### 1. Get a Discord Bot Token

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) and log in
2. Click **"New Application"**, give it a name, click **Create**
3. Go to the **"Bot"** tab in the left sidebar
4. Click **"Reset Token"** and copy the token (you only see it once!)
5. Scroll down to **"Privileged Gateway Intents"** and enable all three:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
6. Click **Save Changes**

### 2. Invite the Bot to Your Server

1. In the Developer Portal, go to **"OAuth2" > "URL Generator"**
2. Under **Scopes**, check **bot**
3. Under **Bot Permissions**, check: Connect, Speak, Send Messages, Read Message History
4. Copy the generated URL and open it in your browser to invite the bot

### 3. Configure and Run

1. Open the `dist/` folder -- this is all you need
2. Open `config.txt` (located next to `MusicBot.exe`) in any text editor and replace `your_bot_token_here` with your actual token:

```
TOKEN=paste_your_bot_token_here
```

The other settings have working defaults and can be left as-is. Only change them if you know what you're doing.

3. Double-click **`MusicBot.exe`** to start the bot. On the first launch it will automatically download FFmpeg (~80 MB) -- this only happens once.

Once you see a message like `We have logged in as YourBot#1234`, the bot is online and ready.

> **Note:** You do not need to install Python, any packages, or any other dependencies. Everything is bundled inside `MusicBot.exe`.

---

## Commands

All commands use the `!` prefix.

| Command    | Description                                    |
|------------|------------------------------------------------|
| `!play`    | Play a song by search query or YouTube link    |
| `!pause`   | Pause the current song                         |
| `!resume`  | Resume a paused song                           |
| `!stop`    | Stop playback and clear the queue              |
| `!skip`    | Skip to the next song in the queue             |
| `!queue`   | View the current song queue                    |
| `!lyric`   | Show lyrics for the current song               |
| `!mostplayed` | Show the most played songs on the server    |
| `!join`    | Make the bot join your voice channel            |
| `!leave`   | Make the bot leave the voice channel            |
| `!help`    | Show help with a random tip                    |

---

## Config Options (config.txt)

| Key                    | Description                              | Default |
|------------------------|------------------------------------------|---------|
| `TOKEN`                | Your Discord bot token (required)        | -       |
| `FFMPEG_BEFORE_OPTIONS`| FFmpeg input options                     | `-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5` |
| `FFMPEG_OPTIONS`       | FFmpeg output options                    | `-vn`   |
| `YDL_FORMAT`           | Audio format preference                  | `bestaudio` |
| `FFMPEG_URL`           | Download URL for FFmpeg (auto-install)   | `https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip` |

Lines starting with `#` are treated as comments and ignored.

---

## Building from Source (developers only)

If you want to modify the code and rebuild the executable yourself, you will need Python 3.10+ installed.

```bash
pip install -r requirements.txt
build.bat
```

This will produce a fresh `MusicBot.exe` in the `dist/` folder.

### Project Structure

```
MusicBot/
├── run.py                       # entry point
├── src/
│   ├── main.py                  # bot setup, events, help command
│   ├── cogs/
│   │   └── music.py             # all music commands
│   └── utils/
│       ├── config_loader.py     # config.txt parser
│       ├── ffmpeg_setup.py      # ffmpeg auto-download
│       └── song_db.py           # JSON song play tracker
├── config.txt                   # bot configuration
├── build.bat                    # build script
├── requirements.txt             # Python dependencies
└── README.md
```

---

## Troubleshooting

- **Bot doesn't respond to commands** -- Make sure Message Content Intent is enabled in the Developer Portal.
- **Bot won't join voice** -- Make sure it has Connect and Speak permissions in your server.
- **No sound** -- FFmpeg may have failed to download. Check that `ffmpeg.exe` exists next to `MusicBot.exe`. If not, download it manually from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/) and place `ffmpeg.exe` in the same folder.
- **"ERROR: Please set your bot token in config.txt"** -- Open `config.txt` and set your token.
