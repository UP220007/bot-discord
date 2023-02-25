import discord
from discord.ext import commands
from pytube import YouTube
import asyncio
from discord.ext import tasks
import os
from dotenv import load_dotenv
from pytube import Playlist
from discord.utils import get
#codigo con funciones de musica funcionales trabajando correctamente 
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
voice_channel = None
is_paused = False
queue = []
current = ""
playing = False

load_dotenv()
token = os.environ.get('DANG')

async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    game = discord.Game("Escuchando !dhelp")
    await bot.change_presence(activity=game)

@bot.command(name='play', description='agrega una cancion o lista de youtube a la cola de reproduccion')
async def play(ctx, url):
    channel = ctx.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    global playing
    global queue
    global current 

    if 'list=' in url:
        playlist_id = url.split('list=')[1]
        playlist = Playlist('https://www.youtube.com/playlist?list=' + playlist_id)
        video_urls = playlist.video_urls

        # Agregar las URLs de la lista de reproducción a la cola
        queue += video_urls

        if not playing:
            # Si no se está reproduciendo nada, iniciar la reproducción de la primera canción en la cola
            playing = True
            while len(queue) > 0:
                next_video_url = queue.pop(0)
                video = YouTube(next_video_url)
                audio_stream = video.streams.filter(only_audio=True).first()
                voice.play(discord.FFmpegPCMAudio(audio_stream.download()), after=lambda e: print('done', e))
                await ctx.send(f"Reproduciendo {video.title}...")
                current = video.title 
                while voice.is_playing() or voice.is_paused():
                    await asyncio.sleep(1)
                await ctx.send(f"Terminó la reproducción de {video.title}.")
            playing = False

    else:
        # Agregar la URL de la canción a la cola
        queue.append(url)

        if not playing:
            # Si no se está reproduciendo nada, iniciar la reproducción de la primera canción en la cola
            playing = True
            while len(queue) > 0:
                next_video_url = queue.pop(0)
                video = YouTube(next_video_url)
                audio_stream = video.streams.filter(only_audio=True).first()
                voice.play(discord.FFmpegPCMAudio(audio_stream.download()), after=lambda e: print('done', e))
                await ctx.send(f"Reproduciendo {video.title}...")
                current = video.title 
                while voice.is_playing() or voice.is_paused():
                    await asyncio.sleep(1)
                await ctx.send(f"Terminó la reproducción de {video.title}.")
            playing = False

@bot.command(name='pause', description='pone en pausa  la reproduccion del video actual')
async def pause(ctx):
    global is_paused
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        is_paused = True
        await ctx.send('Música en pausa.')
    else:
        await ctx.send('No hay música reproduciéndose actualmente.')

@bot.command(name='resume',  description='reanuda la repduccion de la cancion pausada')
async def resume(ctx):
    global is_paused
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        is_paused = False
        await ctx.send('Reproducción de música reanudada.')
    else:
        await ctx.send('No hay música pausada actualmente.')

@bot.command(name='stop', description='detiene toda repduccion y borra la cola')
async def stop(ctx):
    # Obtener el cliente de voz
    voice = get(bot.voice_clients, guild=ctx.guild)
    # Detener la música y borrar la lista de reproducción
    if voice and voice.is_playing():
        voice.stop()
    queue.clear()
    global current
    current=""
    await ctx.send("Música detenida y lista de reproducción borrada.")


@bot.command(name='next', description='pasa al siguiente video de la cola')
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
    await play_next_song(ctx, voice)

@bot.command(name='join', description='se une al canal de voz en el que este el ussssuario')
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.send(f'Conectado al canal de voz: {channel}')

@bot.command(name='leave', description='desconecta al bot del canal de voz')
async def leave(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send('Saliendo del canal de voz')
    else:
        await ctx.send('No estoy conectado a un canal de voz.')

@bot.command(name='list', description='muestra la cancion en reproduccion y las 10 siguientes')
async def list_songs(ctx):
    songs = []
    songs.clear()
    try:
        #url2 = queue[0]
        #video = YouTube(url2)
        #title = video.title
        #current_song = title
        current_song = current
        voice = get(bot.voice_clients, guild=ctx.guild)
        if not voice or not voice.is_playing():
            if is_paused: 
                for i, url in enumerate(queue[:10]):
                    video = YouTube(url)
                    title = video.title
                    songs.append(f"{i+1}. {title}")
                embed = discord.Embed(title=f"Canciones en la cola ({len(queue)}):", description=f"Actualmente reproduciendo: **{current_song}**\n\n" + "\n".join(songs), color=0xff0000)
                await ctx.send(embed=embed)
            else:
                if current=="":
                    embed = discord.Embed(title=f"Canciones en la cola ({len(queue)}):", description=f"No hay canciones en la cola actual.", color=0xff0000)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"Canciones en la cola ({len(queue)}):", description=f"Actualmente reproduciendo: **{current_song}**\n\ No hay canciones en la cola actual.", color=0xff0000)
                    await ctx.send(embed=embed)
            return
        for i, url in enumerate(queue[:10]):
            video = YouTube(url)
            title = video.title
            songs.append(f"{i+1}. {title}")
        if len(queue)==0 :
            embed = discord.Embed(title=f"Canciones en la cola (1):", description=f"Actualmente reproduciendo: **{current_song}**\n\n No hay canciones en la cola actual.", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"Canciones en la cola ({len(queue)}):", description=f"Actualmente reproduciendo: **{current_song}**\n\n" + "\n".join(songs), color=0xff0000)
            await ctx.send(embed=embed)
        #embed = discord.Embed(title=f"Canciones en la cola ({len(queue)}):", description=f"Actualmente reproduciendo: **{current_song}**\n\n" + "\n".join(songs), color=0xff0000)
        #await ctx.send(embed=embed)
    except Exception as e:
        print(f"Se produjo un error al ejecutar el comando 'list': {e}")

bot.remove_command('dhelp')
bot.remove_command('help')

@bot.command(name='dhelp', description='muestra todos los comandos del bot')
async def help_command(ctx):
    embed = discord.Embed(
        title="Comandos del bot",
        description="Aquí está una lista de todos los comandos del bot y su descripción:",
        color=discord.Color.green()
    )
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.description, inline=False)
    await ctx.send(embed=embed)

#bot.run('OTg4OTE1MzczNDQzMjgwODk2.GT3SxN.PM7PDyaQ9CHUEQntB_0OZEPvtWFSN2ju0BDLA4')

bot.run(token)#token de dang https://discord.com/api/oauth2/authorize?client_id=988915373443280896&permissions=8&scope=bot
#bot.run('OTg4OTM1MTcyNTE2ODgwNDA0.GMSsjK.V-PS_oO1hTXm9Qv4R9pheU2GKx4QIKpn2MAFY4')#token de dong https://discord.com/api/oauth2/authorize?client_id=988935172516880404&permissions=8&scope=bot
#bot.run("OTg4Mjc0NDYwNTQzMDQ1Njky.GSkAmH.gDfMnxjJoijq1SX7rTRhyov9WgLW4J6STMWJHw")#token de ding https://discord.com/api/oauth2/authorize?client_id=988274460543045692&permissions=8&scope=bot
