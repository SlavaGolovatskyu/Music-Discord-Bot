import asyncio
import functools
import discord                                                                              
from discord.ext.commands import bot       
from discord.ext import commands
from asyncio import sleep
import urllib.parse
import urllib.request
import re
import yt_dlp as youtube_dl
import aiohttp
from config_loader import load_config

_config = load_config()

# Defaults
_DEFAULT_FFMPEG_BEFORE = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
_DEFAULT_FFMPEG_OPTS   = '-vn'
_DEFAULT_YDL_FORMAT    = 'bestaudio'

FFMPEG_OPTIONS = {
    'before_options': _config.get('FFMPEG_BEFORE_OPTIONS', _DEFAULT_FFMPEG_BEFORE),
    'options': _config.get('FFMPEG_OPTIONS', _DEFAULT_FFMPEG_OPTS),
}
YDL_OPTIONS = {
    'format': _config.get('YDL_FORMAT', _DEFAULT_YDL_FORMAT),
    'noplaylist': True,
}

Queue = {}

# Regex to detect YouTube URLs
_YT_URL_RE = re.compile(
    r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\S]+'
)


def _clean_youtube_url(url):
    """Strip playlist/index params from a YouTube URL so yt_dlp treats it as a single video."""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    # Keep only the video ID parameter
    clean_params = {}
    if 'v' in params:
        clean_params['v'] = params['v'][0]
    clean_query = urllib.parse.urlencode(clean_params)
    return urllib.parse.urlunparse(parsed._replace(query=clean_query))


def _extract_info_sync(ydl_opts, url):
    """Run yt_dlp extract_info synchronously (to be called via run_in_executor)."""
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def _search_youtube_sync(query):
    """Run YouTube search synchronously (to be called via run_in_executor)."""
    query_string = urllib.parse.urlencode({'search_query': query})
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(
        r"watch\?v=(\S{11})", htm_content.read().decode())
    return search_results


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command() 
    async def stop(self, ctx):
        if ctx.author.voice:
            if ctx.voice_client:
                voice = ctx.guild.voice_client
                if ctx.guild.id in Queue:
                    Queue[ctx.guild.id].clear()
                voice.stop()
                await ctx.send("All music stopped and deleted from Queue!")
            else:
                await ctx.send("I am not in a voice channel!")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")
    
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            await ctx.send("Connected to a voice channel")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")
    
    @commands.command()
    async def leave(self, ctx):
        if ctx.author.voice:
            if ctx.voice_client:
                await ctx.send("Leaving the voice channel")
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("I am not in a voice channel!")  
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")
    
    @commands.command(pass_context=True)
    async def pause(self, ctx):
        if (ctx.author.voice):
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_playing():
                voice.pause()
                await ctx.send("**Selection paused.**")
                await sleep(300)
                if ctx.voice_client and ctx.guild.voice_client.is_paused():
                    await ctx.send("Paused for too long!")
                    await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("There is no music to pause!")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        if (ctx.author.voice):
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_paused():
                voice.resume()
                await ctx.send("**Selection resumed.**")
            else:
                await ctx.send("There is no song to resume!")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")

    @commands.command()
    async def queue(self, ctx, page_num=1):
        embed = discord.Embed(color=0xa09c9c)
        if ctx.guild.id not in Queue or len(Queue[ctx.guild.id]) == 0:
            return await ctx.send("No queue!")
        real_num = page_num - 1
        queue_pages = []
        page = []
        k = 1
        for i in range(len(Queue[ctx.guild.id])):
            page.append(Queue[ctx.guild.id][i])
            if k % 10 == 0:
                temp = page.copy()
                queue_pages.append(temp)
                page.clear()
            elif (k == len(Queue[ctx.guild.id])) and (k % 10 != 0):
                queue_pages.append(page)
            k = k + 1

        if (page_num > len(queue_pages)) or (page_num <= 0):
            return await ctx.send("Invalid page number. There are currently " + str(len(queue_pages)) + " page(s) in the queue.")

        embed.title = "**Current queue**"
        key = page_num - 1
        for j in range(len(queue_pages[real_num])):
            if page_num == 1:
                if j == 0:
                    embed.add_field(name="[0] is Playing:", value=queue_pages[real_num][j].get('title', None), inline=False)
                else:
                    embed.add_field(name=str(j) + ". ", value=queue_pages[real_num][j].get('title', None), inline=False)
            else:
                embed.add_field(name=str(key) + str(j) + ". ", value=queue_pages[real_num][j].get('title', None), inline=False)

        embed.set_footer(text="Page " + str(page_num) +"/" + str(len(queue_pages)))
        await ctx.send(embed=embed)
    
    @commands.command()
    async def skip(self, ctx, index=0):
        if ctx.author.voice:
            voice = ctx.guild.voice_client
            if not voice:
                return await ctx.send("I am not in a voice channel!")
            if ctx.guild.id not in Queue or len(Queue[ctx.guild.id]) == 0:
                return await ctx.send("No songs in the queue!")
            if index >= len(Queue[ctx.guild.id]):
                return await ctx.send("Out of range, can't skip song!")
            if len(Queue[ctx.guild.id]) == 1:
                return await ctx.send("Can't skip song, min: 2 songs in queue!")
            if index == 0:
                voice.stop()
            else:
                del Queue[ctx.guild.id][index]
            await ctx.send("Song skipped!")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def automatic_play(self, ctx):
        if ctx.guild.id not in Queue or len(Queue[ctx.guild.id]) == 0:
            await ctx.send("No song in queue")
            return
        if not (ctx.voice_client):
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            voice = ctx.guild.voice_client

        # Run extract_info in a thread so it doesn't block the event loop
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            functools.partial(_extract_info_sync, YDL_OPTIONS, Queue[ctx.guild.id][0]['webpage_url'])
        )
        url2 = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        voice.play(source)
        
        while (voice.is_playing() or voice.is_paused()):
            await sleep(1)
        del(Queue[ctx.guild.id][0])
        if len(Queue[ctx.guild.id]) != 0:
            await self.bot.get_command('automatic_play').callback(self, ctx)
        else:
            Queue.pop(ctx.guild.id, None)
            await voice.disconnect()
    
    @commands.command()
    async def play(self, ctx, *, search):
        # Detect direct YouTube URLs instead of always searching
        yt_match = _YT_URL_RE.match(search.strip())
        if yt_match:
            url = search.strip()
            if not url.startswith('http'):
                url = 'https://' + url
            # Strip playlist/index params so only the single video is extracted
            url = _clean_youtube_url(url)
        else:
            # Run YouTube search in a thread so it doesn't block the event loop
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None,
                functools.partial(_search_youtube_sync, search)
            )
            
            if not search_results:
                return await ctx.send("No results found for your search!")
            
            url = 'http://www.youtube.com/watch?v=' + search_results[0]
        
        if (ctx.author.voice):
            # Connect to voice FIRST — if this fails we bail out before touching the queue
            if not (ctx.voice_client):
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
            else:
                voice = ctx.guild.voice_client

            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'format': 'bestaudio/best',
                'noplaylist': True,
            }

            # Run extract_info in a thread so it doesn't block the event loop
            loop = asyncio.get_event_loop()
            await ctx.send("Loading song info...")
            info = await loop.run_in_executor(
                None,
                functools.partial(_extract_info_sync, ydl_opts, url)
            )

            # Only create / append to queue AFTER voice + info succeeded
            if ctx.guild.id not in Queue:
                Queue[ctx.guild.id] = []
            Queue[ctx.guild.id].append(
                {'webpage_url': info['webpage_url'], 'title': info['title']})

            if len(Queue[ctx.guild.id]) == 1:
                await ctx.send(f'Now play ***{Queue[ctx.guild.id][0]["title"]}***\nSong added to queue')
            if len(Queue[ctx.guild.id]) >= 2:
                await ctx.send(f"Song added to queue! : [***{Queue[ctx.guild.id][-1]['title']}***]")
            
            if not (voice.is_playing() or voice.is_paused()):
                await self.bot.get_command('automatic_play').callback(self, ctx)
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")
            
    @commands.command()
    async def lyric(self, ctx):
        if ctx.author.voice:
            if ctx.guild.id not in Queue or len(Queue[ctx.guild.id]) == 0:
                return await ctx.send("No song is currently playing!")
            sng = Queue[ctx.guild.id][0]["title"].split('-')
            if len(sng) < 2:
                return await ctx.send(f"Can't parse artist/title from: **{Queue[ctx.guild.id][0]['title']}**")
            async with aiohttp.request("GET", f"https://api.lyrics.ovh/v1/{sng[0]}/{sng[1]}", headers={}) as r:
                if r.status != 200:
                    return await ctx.send(f"No lyrics found with this --> **Title** [***{sng[1]}***]")
                data = await r.json()
                embed = discord.Embed(
                    title = sng[1],
                    description = data["lyrics"],
                    colour=0xa09c9c,
                )
                embed.set_author(name=sng[0])
                embed.set_footer(text="Lyric music")
                await ctx.send(embed=embed)
        else:
            return await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")           

async def setup(bot):
    await bot.add_cog(Music(bot))
