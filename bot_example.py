import asyncio
import json
import os
import shutil

import disnake
from disnake.ext import commands

from modules import yandex_music_integration as yami, balaboba_integration as bi
import modules.games.ordinary_games as games
from modules.games.BullsAndCows import *
from modules.games.TicTacToe import *

path_to_music = os.path.join(os.path.abspath(os.path.dirname(__file__)), "music")

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

disnake.opus.load_opus("music/libopus.dylib")


@bot.slash_command(name="ping", description="Pings the bot")
async def ping_command(inter):
    await inter.response.send_message(f"{inter.user.mention}, pong!")


@bot.slash_command(name="roll", description="Rolls the dice")
async def roll_command(
    inter: disnake.ApplicationCommandInteraction, _from: int = 1, _to: int = 6
):
    if _from > _to:
        _from, _to = _to, _from
    await inter.response.send_message(
        f"{inter.user.mention} rolled {random.randint(_from, _to)}!"
    )


@bot.slash_command(
    name="rock-paper-scissors", description="Plays with you in rock paper scissors game"
)
async def play_rock_paper_scissors_command(
    inter: disnake.ApplicationCommandInteraction,
    move: Literal["rock", "paper", "scissors"],
):
    bot_move, result = games.play_rock_paper_scissors(move=move)
    await inter.response.send_message(
        f"{inter.user.mention} played: {move}\n" f"Bot played: {bot_move}\n{result}!"
    )


@bot.slash_command(
    name="bulls-and-cows", description="Plays with you in bulls and cows game"
)
async def play_bulls_and_cows_command(inter: disnake.ApplicationCommandInteraction):
    def is_guess_correct(_message: disnake.Message):
        return (
            _message.author == inter.author
            and _message.content.isdigit()
            and len(set(_message.content)) == 4
        )

    await inter.response.send_message(
        f"Game starts now, please enter 4 different digit string,\n"
        f"it can starts with 0!"
    )

    game = BullsAndCows()
    answer = game.answer
    moves_count = 0

    all_fields = ["Move", "Bulls", "Cows"]
    game_stat = {all_fields[i]: [] for i in range(len(all_fields))}
    message = None

    while True:
        try:
            guess_message = await inter.bot.wait_for(
                "message", check=is_guess_correct, timeout=20
            )
            guess = guess_message.content
            moves_count += 1

            if moves_count == 1:
                await inter.followup.send("Previous results:")
                message = inter.channel.last_message

            bulls_count, cows_count = game.compare_guess_and_answer(guess)
            game_stat["Move"].append(guess)
            game_stat["Bulls"].append(bulls_count)
            game_stat["Cows"].append(cows_count)

            embed = disnake.Embed(title=f"__**Game results:**__", color=0x03F8FC)
            for key, value in game_stat.items():
                value_to_str = "\n".join(map(str, value))
                embed.add_field(name=f"**{key}**", value=f"{value_to_str}")

            await inter.followup.edit_message(message.id, embed=embed)
            await guess_message.delete()

            if guess == answer:
                break
        except asyncio.TimeoutError:
            return await inter.followup.send(
                f"Sorry, you took too long. The answer was {answer}."
            )
    await inter.followup.send(
        f"You win, the number is: {answer}, "
        f"it took you {moves_count} move{'' if moves_count % 10 == 1 else 's'}"
    )


@bot.slash_command(name="tic-tac-toe", description="Plays with you in tic tac toe game")
async def play_tic_tac_toe_command(
    inter: disnake.ApplicationCommandInteraction,
    difficulty: Literal["easy", "normal", "hard"],
    mark: Literal["cross", "zero"],
    player_go_first: Literal["yes", "no"],
):
    field = TicTacToeField()
    player = TicTacToePlayer(mark=mark, field=field)
    bot_mark = [arg for arg in get_args(Literal["cross", "zero"]) if arg != mark][0]
    game_bot = TicTacToeBot(difficulty=difficulty, mark=bot_mark, field=field)
    game = TicTacToeGame(player_1=player, player_2=game_bot, field=field)


# @bot.slash_command(description='test')
# async def test(self, slash_inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
#     view = CustomView(member)
#     button1 = BlurpleButton("TEST")
#     view.add_item(button1)
#
#     async def button_callback(button_inter: disnake.MessageInteraction):
#         button1.disabled = True
#         await button_inter.send(embed=embedname2)
#         await slash_inter.edit_original_message(view=view)
#
#     button1.callback = button_callback
#
#     await slash_inter.send(embed=embed1, view=view)


@bot.slash_command(
    name="guess-number", description="Plays with you in guess number game"
)
async def play_guess_number_command(
    inter: disnake.ApplicationCommandInteraction, _from: int = 1, _to: int = 10
):
    await inter.response.send_message(f"Guess a number between {_from} and {_to}.")

    def is_guess_message(message: disnake.Message):
        return message.author == inter.author and message.content.isdigit()

    if _from > _to:
        _from, _to = _to, _from
    answer = random.randint(_from, _to)

    try:
        guess = await inter.bot.wait_for("message", check=is_guess_message, timeout=10)
    except asyncio.TimeoutError:
        return await inter.followup.send(
            f"Sorry, you took too long. The answer was {answer}."
        )

    if int(guess.content) == answer:
        await inter.followup.send("You guessed correctly!")
    else:
        await inter.followup.send(f"Oops. It is actually {answer}.")


@bot.slash_command(
    name="balaboba", description="Uses balaboba to generate you a random text"
)
async def generate_text_command(
    inter: disnake.ApplicationCommandInteraction,
    text: str,
    language: Literal["en", "ru"] = "ru",
):
    await inter.response.defer()
    response = await bi.generate_text(text, language)
    await inter.followup.send(f"{bot.user.mention} your generated text is:\n{response}")


async def clean_music_folder():
    shutil.rmtree(f"{path_to_music}/songs")
    shutil.rmtree(f"{path_to_music}/albums")
    shutil.rmtree(f"{path_to_music}/podcasts")
    shutil.rmtree(f"{path_to_music}/podcast_episodes")


async def is_available_to_connect(inter: disnake.ApplicationCommandInteraction) -> bool:
    # user does not sit in any channel
    if inter.user.voice is None:
        await inter.response.send_message(f"you should be in a voice channel")
        return False
    # bot is already sits in another channel
    if (
        inter.guild.voice_client is not None
        and inter.me.voice.channel != inter.user.voice.channel
    ):
        await inter.response.send_message(f"bot sits in another voice channel")
        return False
    return inter.guild.voice_client is None


async def play_track(
    inter: disnake.ApplicationCommandInteraction,
    voice_client: disnake.VoiceClient,
    track: yami.TrackInfo,
):
    await inter.followup.send(f"now is playing song: {track.title}")
    voice_client.play(
        disnake.FFmpegPCMAudio(f"{track.short_path}"),
        after=print("done"),
    )
    while voice_client.is_playing():
        await asyncio.sleep(1)
    voice_client.stop()


async def play(
    inter: disnake.ApplicationCommandInteraction, voice_client: disnake.VoiceClient
):
    for volume in yami.YAM().track_list:
        if isinstance(volume, yami.TrackInfo):
            await play_track(inter=inter, voice_client=voice_client, track=volume)
        else:
            await inter.followup.send(f"now is playing album: {volume.title}")
            for track in volume.tracks:
                await play_track(inter=inter, voice_client=voice_client, track=track)

    await voice_client.disconnect()
    await clean_music_folder()


# @bot.slash_command(name="yam-play-song", description="Search for song in yandex music")
# async def yam_play_song_command(inter, song_name: str):
#     if inter.user.voice is None:
#         return await inter.response.send_message(f"you should be in a voice channel")
#     if inter.user.voice.channel.guild.voice_client is None:
#         yam_class = yami.YAM()
#         song_title = await yam_class.download_song_by_name(song_name=song_name)
#
#         vc = await inter.user.voice.channel.connect()
#         await inter.response.send_message(f"bot is playing: {song_title}")
#
#         vc.play(disnake.FFmpegPCMAudio(f'music/songs/{song_title}.mp3'), after=lambda e: print('done', e))
#         while vc.is_playing():
#             await asyncio.sleep(1)
#         vc.stop()
#         await clean_music_folder()
#         return await vc.disconnect()
#     if inter.user.voice.channel.guild.voice_client.is_connected():
#         return await inter.response.send_message(f"bot sits in another voice channel")
#
#
# @bot.slash_command(name="yam-play-album", description="Search for album in yandex music")
# async def yam_play_album_command(inter, album_name: str):
#     if inter.user.voice is None:
#         return await inter.response.send_message(f"you should be in a voice channel")
#     if inter.user.voice.channel.guild.voice_client is None:
#         await inter.response.defer()
#         # проблема - ждет загрузки всех треков из альбома,
#         # нужно, чтобы дожидался загрузки хотя бы одного и сразу же его запускал
#         album_title = await yami.YAM().download_album_by_name(album_name=album_name)
#
#         vc = await inter.user.voice.channel.connect()
#         await inter.followup.send(f"bot is playing: {album_title}")
#
#         path_to_album_songs = os.path.join(os.path.abspath(os.path.dirname(__file__)),
#                                            f'music/albums/{album_title}')
#         for track_name in os.listdir(path_to_album_songs):
#             vc.play(disnake.FFmpegPCMAudio(f'{path_to_album_songs}/{track_name}'),
#                     after=lambda e: print('done', e))
#             while vc.is_playing():
#                 await asyncio.sleep(1)
#             vc.stop()
#         await clean_music_folder()
#         return await vc.disconnect()
#     if inter.user.voice.channel.guild.voice_client.is_connected():
#         return await inter.response.send_message(f"bot sits in another voice channel")


@bot.slash_command(name="yam-play", description="Search in yandex music")
async def yam_play_command(
    inter: disnake.ApplicationCommandInteraction,
    _type: Literal["track", "album", "podcast episode", "podcast"],
    name: str,
):
    if await is_available_to_connect(inter):
        vc = await inter.user.voice.channel.connect(timeout=80)
        await inter.response.send_message(f"bot connected to the channel")
    else:
        vc = bot.voice_clients[0]
    # upload track/album/podcast... if can find at least one -> return True,
    # otherwise -> return False
    if not await yami.YAM().download(name=name, _type=_type):
        return await inter.followup.send(f"bot couldn't find anything")

    if not vc.is_playing():
        await play(inter=inter, voice_client=vc)
    else:
        await inter.response.send_message(
            f"{yami.YAM.track_list[-1].title} added to queue."
        )


@bot.slash_command(name="yam-stop", description="Stop playing music")
async def stop_command(inter: disnake.ApplicationCommandInteraction):
    # check if bot is on channel
    if inter.user.voice is None:
        return await inter.response.send_message(f"bot is already left all channels")
    # stop queue
    # clean all folders
    await clean_music_folder()
    await inter.user.voice.channel.guild.voice_client.disconnect(force=False)
    await inter.response.send_message(f"bot disconnected from a voice channel")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    with open("configuration.json") as json_data_file:
        data = json.load(json_data_file)
    bot_data = data["bot"]
    bot.run(bot_data["token"])
