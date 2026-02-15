import random
import discord
from discord.ext.commands import bot
from discord.ext import commands
from src.utils.config_loader import load_config
from src.utils.ffmpeg_setup import ensure_ffmpeg

config = load_config()
TOKEN = config.get("TOKEN", "")

# Download ffmpeg automatically if not present
ensure_ffmpeg()

prefix = "!"
intents=discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game("Bot music [HALAL!]"))
    print("We have logged in as {0.user}\nHappy dugem. [HALAL!]".format(bot))
    await bot.load_extension('src.cogs.music')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith(prefix+'automatic_play'):
        return
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.qualified_name == "play":
            await ctx.send(f"{prefix}play [query|link musik]")
        else:
            await ctx.send("Missing required argument!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command is unreachable")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have enough permission!")
    else:
        print(f"[ERROR] {ctx.command}: {error}")
        await ctx.send(f"An error occurred: {error}")

@bot.command(invoke_without_command = True)
async def help(ctx):
    tip = [" - !play (query or link) to play a music", " - DM iFanpS#5409 if u want to contribute", " - Use headphone for better experience"
           " - Don't leave while bot is playing a music, bot will sad ;(", " - Listening music together will be fun"]
    await ctx.send("Tip"+random.choice(tip)+"\n")
    embed = discord.Embed(title = "***Help***", color = 0xa09c9c)
    embed.add_field(name = "General", value = "ping | purge", inline=False)
    embed.add_field(name = "Music", value = "lyric | play | stop | queue | pause | resume | mostplayed", inline=False)
    embed.set_footer(text = "Help Menu")
    await ctx.send(embed = embed)


def run():
    if not TOKEN or TOKEN == "your_bot_token_here":
        print("ERROR: Please set your bot token in config.txt")
    else:
        bot.run(TOKEN)
