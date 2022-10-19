import asyncio
import json
import random
import os

import disnake
from disnake.ext import commands

from typing import Literal
import balaboba_integration as bi

import yandex_music_integration as yami

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
    await inter.response.send_message(f"{inter.user} pong!")


@bot.slash_command(name="roll", description="Rolls the dice")
async def roll_command(inter, _from: int = 1, _to: int = 6):
    await inter.response.send_message(f"{inter.user} rolled {random.randint(_from, _to)}!")


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
    if move.lower() not in list_of_moves:
        return await inter.response.send_message(f"You entered wrong word, "
                                                 f"bot accepts only these words: {list_of_moves}")
    bot_move = random.choice(list_of_moves)
    await inter.response.send_message(f"{inter.user.mention} played: {move}\n"
                                      f"Bot played: {bot_move}\n{get_game_result(move, bot_move)}!")


@bot.slash_command(name="bulls-and-cows", description="Plays with you in bulls and cows game")
async def play_bulls_and_cows_command(inter):
    def generate_number_for_bulls_and_cows_game():
        all_numbers = [str(x) for x in range(10)]
        result = ''
        for i in range(4):
            number = random.choice(all_numbers)
            result += number
            all_numbers.remove(number)
        return result

    def is_guess_correct(message: disnake.Message):
        return message.author == inter.author and message.content.isdigit() and len(message.content) == 4

    def compare_guess_and_answer(_answer: str, _guess: str):
        bulls_count = 0
        cows_count = 0
        for i in range(4):
            # find pos of guess[i] symbol in answer
            pos = _answer.find(_guess[i])
            # has symbol and it has same position
            if pos == i:
                bulls_count += 1
            # has symbol, but its position is different
            elif pos != -1:
                cows_count += 1
        return f"bulls: {bulls_count}, cows: {cows_count}"

    await inter.response.send_message(f"Game starts now, please enter 4 digit str, it can starts with 0!\n")

    answer = generate_number_for_bulls_and_cows_game()
    moves_count = 0

    while True:
        try:
            guess = await inter.bot.wait_for("message", check=is_guess_correct, timeout=40)
            moves_count += 1
            if guess.content == answer:
                break
            result_of_compare = compare_guess_and_answer(answer, guess.content)
            await guess.reply(f"result of previous guess is:\nYou entered: " +
                              guess.content + "\n" + result_of_compare)
            await guess.delete()
        except asyncio.TimeoutError:
            return await inter.followup.send(f"Sorry, you took too long. The answer was {answer}.")

    await inter.followup.send(f"You win, the number is: {answer}, "
                              f"it took you {moves_count} move{'' if moves_count % 10 == 1 else 's'}")


@bot.slash_command(name="guess-number", description="Plays with you in guess number game")
async def play_guess_number_command(inter, _from: int = 1, _to: int = 10):
    await inter.response.send_message(f"Guess a number between {_from} and {_to}.")

    def is_guess_message(message: disnake.Message):
        return message.author == inter.author and message.content.isdigit()

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
    os.rmdir(f"{path_to_music}/songs")
    os.rmdir(f"{path_to_music}/albums")


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
        yam_class = yami.YAM()
        album_title = await yam_class.download_album_by_name(album_name=album_name)

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


@bot.slash_command(name="stop_yam", description="Stop playing music")
async def stop_command(inter):
    if inter.user.voice is None:
        return await inter.response.send_message(f"bot is already left all channels")
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
