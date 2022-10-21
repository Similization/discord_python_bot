import asyncio
import json
import random
import os
import shutil

import disnake
from disnake.ext import commands

from typing import Literal

from modules import yandex_music_integration as yami, balaboba_integration as bi

path_to_music = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'music')

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents
)

disnake.opus.load_opus('music/libopus.dylib')


@bot.slash_command(name="ping", description="Pings the bot")
async def ping_command(inter):
    await inter.response.send_message(f"{inter.user.mention}, pong!")


@bot.slash_command(name="roll", description="Rolls the dice")
async def roll_command(inter, _from: int = 1, _to: int = 6):
    # if not isinstance(_from, int) and not isinstance(_to, int):
    #     return await inter.response.send_message(f"bot will accept only integer arguments for this command")
    if _from > _to:
        _from, _to = _to, _from
    await inter.response.send_message(f"{inter.user.mention} rolled {random.randint(_from, _to)}!")


@bot.slash_command(name="rock-paper-scissors", description="Plays with you in rock paper scissors game")
async def play_rock_paper_scissors_command(inter, move: Literal['rock', 'paper', 'scissors']):
    def get_game_result(player_move: str, _bot_move: str):
        if player_move == _bot_move:
            return "Draw"
        elif player_move == "rock":
            if _bot_move == "scissors":
                return "You win"
            else:
                return "Bot wins"
        elif player_move == "paper":
            if _bot_move == "rock":
                return "You win"
            else:
                return "Bot wins"
        elif player_move == "scissors":
            if _bot_move == "paper":
                return "You win"
            else:
                return "Bot wins"

    list_of_moves = ['rock', 'paper', 'scissors']
    # if move not in list_of_moves:
    #     return await inter.response.send_message(f"You entered wrong word, "
    #                                              f"bot accepts only these words: {list_of_moves}")
    bot_move = random.choice(list_of_moves)
    await inter.response.send_message(f"{inter.user.mention} played: {move}\n"
                                      f"Bot played: {bot_move}\n{get_game_result(move, bot_move)}!")


@bot.slash_command(name="bulls-and-cows", description="Plays with you in bulls and cows game")
async def play_bulls_and_cows_command(inter):
    def generate_number_for_bulls_and_cows_game():
        all_numbers = [str(x) for x in range(10)]
        result = ''.join(random.sample(all_numbers, 4))
        # for i in range(4):
        #     number = random.choice(all_numbers)
        #     result += number
        #     all_numbers.remove(number)
        return result

    def is_guess_correct(_message: disnake.Message):
        return _message.author == inter.author and \
               _message.content.isdigit() and \
               len(set(_message.content)) == 4

    def compare_guess_and_answer(_answer: str, _guess: str):
        _bulls_count = 0
        _cows_count = 0
        for i in range(4):
            # find pos of guess[i] symbol in answer
            pos = _answer.find(_guess[i])
            # has symbol and it has same position
            if pos == i:
                _bulls_count += 1
            # has symbol, but its position is different
            elif pos != -1:
                _cows_count += 1
        return _bulls_count, _cows_count

    await inter.response.send_message(f"Game starts now, please enter 4 different digit string,\n"
                                      f"it can starts with 0!")

    answer = generate_number_for_bulls_and_cows_game()
    moves_count = 0

    all_fields = ["Move", "Bulls", "Cows"]
    game_stat = {all_fields[i]: [] for i in range(len(all_fields))}
    message = None

    while True:
        try:
            guess_message = await inter.bot.wait_for("message", check=is_guess_correct, timeout=20)
            guess = guess_message.content
            moves_count += 1

            if moves_count == 1:
                await inter.followup.send("Previous results:")
                message = inter.channel.last_message

            bulls_count, cows_count = compare_guess_and_answer(answer, guess)
            game_stat["Move"].append(guess)
            game_stat["Bulls"].append(bulls_count)
            game_stat["Cows"].append(cows_count)

            embed = disnake.Embed(title=f"__**Game results:**__", color=0x03f8fc)
            for key, value in game_stat.items():
                value_to_str = "\n".join(map(str, value))
                embed.add_field(name=f'**{key}**',
                                value=f'{value_to_str}')

            await inter.followup.edit_message(message.id, embed=embed)
            await guess_message.delete()

            if guess == answer:
                break
        except asyncio.TimeoutError:
            return await inter.followup.send(f"Sorry, you took too long. The answer was {answer}.")
    await inter.followup.send(f"You win, the number is: {answer}, "
                              f"it took you {moves_count} move{'' if moves_count % 10 == 1 else 's'}")


@bot.slash_command(name="guess-number", description="Plays with you in guess number game")
async def play_guess_number_command(inter, _from: int = 1, _to: int = 10):
    await inter.response.send_message(f"Guess a number between {_from} and {_to}.")

    def is_guess_message(message: disnake.Message):
        return message.author == inter.author and message.content.isdigit()

    if _from > _to:
        _from, _to = _to, _from
    answer = random.randint(_from, _to)

    try:
        guess = await inter.bot.wait_for("message", check=is_guess_message, timeout=10)
    except asyncio.TimeoutError:
        return await inter.followup.send(f"Sorry, you took too long. The answer was {answer}.")

    if int(guess.content) == answer:
        await inter.followup.send("You guessed correctly!")
    else:
        await inter.followup.send(f"Oops. It is actually {answer}.")


@bot.slash_command(name="balaboba", description="Uses balaboba to generate you a random text")
async def generate_text_command(inter, text: str, language: Literal["en", "ru"] = "ru"):
    await inter.response.defer()
    response = await bi.generate_text(text, language)
    await inter.followup.send(f"{bot.user.mention} your generated text is:\n{response}")


async def clean_music_folder():
    shutil.rmtree(f"{path_to_music}/songs")
    shutil.rmtree(f"{path_to_music}/albums")


async def is_available_to_work_with_music(inter) -> bool:
    # проверка на то, что бота можно подключить к голосовому каналу
    # 1 бот никуда не подключен - надо подключить
    # 2 если бот уже подключен - надо проверить, к какому каналу и  только в этом случае сказать, что все хорошо
    # user does not sit in any channel
    if inter.user.voice is None:
        await inter.response.send_message(f"you should be in a voice channel")
        return False
    # bot is already sits in another channel
    if inter.user.voice.channel.guild.voice_client.is_connected():
        await inter.response.send_message(f"bot sits in another voice channel")
        return False
    return True


async def play_track(inter, track: yami.TrackInfo):
    # если музыка еще не играет - нужно запустить
    vc = await inter.user.voice.channel.connect()
    await inter.response.send_message(f"now is playing song: {track.title}")
    vc.play(disnake.FFmpegPCMAudio(f'{track.short_path}'), after=lambda e: print('done', e))
    while vc.is_playing():
        await asyncio.sleep(1)
    vc.stop()


async def play_songs(inter):
    # есть список треков - yami.YAM().track_list
    # нужно пройтись по нему и запустить каждый из треков в порядке очереди,
    # при условии, что треки будут обновляться и новые тоже должны быть запущены
    for volume in yami.YAM().track_list:
        if isinstance(volume, yami.TrackInfo):
            await play_track(inter, volume)
        else:
            await inter.response.send_message(f"now is playing album: {volume.title}")
            for track in volume.tracks:
                await play_track(inter, track)


@bot.slash_command(name="yam-play-song", description="Search for song in yandex music")
async def yam_play_song_command(inter, song_name: str):
    if inter.user.voice is None:
        return await inter.response.send_message(f"you should be in a voice channel")
    if inter.user.voice.channel.guild.voice_client is None:
        yam_class = yami.YAM()
        song_title = await yam_class.download_song_by_name(song_name=song_name)

        vc = await inter.user.voice.channel.connect()
        await inter.response.send_message(f"bot is playing: {song_title}")

        vc.play(disnake.FFmpegPCMAudio(f'music/songs/{song_title}.mp3'), after=lambda e: print('done', e))
        while vc.is_playing():
            await asyncio.sleep(1)
        vc.stop()
        await clean_music_folder()
        return await vc.disconnect()
    if inter.user.voice.channel.guild.voice_client.is_connected():
        return await inter.response.send_message(f"bot sits in another voice channel")


@bot.slash_command(name="yam-play-album", description="Search for album in yandex music")
async def yam_play_album_command(inter, album_name: str):
    if inter.user.voice is None:
        return await inter.response.send_message(f"you should be in a voice channel")
    if inter.user.voice.channel.guild.voice_client is None:
        await inter.response.defer()
        # проблема - ждет загрузки всех треков из альбома,
        # нужно, чтобы дожидался загрузки хотя бы одного и сразу же его запускал
        album_title = await yami.YAM().download_album_by_name(album_name=album_name)

        vc = await inter.user.voice.channel.connect()
        await inter.followup.send(f"bot is playing: {album_title}")

        path_to_album_songs = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                           f'music/albums/{album_title}')
        for track_name in os.listdir(path_to_album_songs):
            vc.play(disnake.FFmpegPCMAudio(f'{path_to_album_songs}/{track_name}'),
                    after=lambda e: print('done', e))
            while vc.is_playing():
                await asyncio.sleep(1)
            vc.stop()
        await clean_music_folder()
        return await vc.disconnect()
    if inter.user.voice.channel.guild.voice_client.is_connected():
        return await inter.response.send_message(f"bot sits in another voice channel")


@bot.slash_command(name="yam-play", description="Search in yandex music")
async def yam_play_command(inter, _type: Literal["track", "album", "podcast episode", "podcast"],
                           name: str):
    # check if we can connect to channel
    # need to upload track/album/podcast...
    await yami.YAM().download(name=name, _type=_type)
    # add to queue


@bot.slash_command(name="yam-stop", description="Stop playing music")
async def stop_command(inter):
    # check if bot is on channel
    if inter.user.voice is None:
        return await inter.response.send_message(f"bot is already left all channels")
    # stop queue
    # clean all folders
    await clean_music_folder()
    await inter.user.voice.channel.guild.voice_client.disconnect()
    await inter.response.send_message(f"bot disconnected from a voice channel")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    with open("configuration.json") as json_data_file:
        data = json.load(json_data_file)
    bot_data = data["bot"]
    bot.run(bot_data["token"])
