import asyncio
import json
import os
import shutil

import disnake
import youtube_dl

from modules import balaboba_integration as bi
from modules.music import yandex_music_integration as yami
import modules.games.ordinary_games as games
from modules.StarBot import StarBot
from modules.games.BullsAndCows import *
from modules.games.TicTacToe import *
from modules.music.MusicQueue import MusicQueue

path_to_music = os.path.join(os.path.abspath(os.path.dirname(__file__)), "music")
yami.YAM.project_path = os.path.abspath(os.path.dirname(__file__))

with open("util/configuration.json") as json_data_file:
    data = json.load(json_data_file)
bot_data = data["bot"]
bot = StarBot(config=bot_data)
bot.music_queue = MusicQueue(inter=None, voice_client=None)


@bot.slash_command(name="ping", description="Pings the bot")
async def ping_command(inter: disnake.ApplicationCommandInteraction):
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
    bot_move, result = await games.play_rock_paper_scissors(move=move)
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

            bulls_count, cows_count = await game.compare_guess_and_answer(guess)
            game_stat["Move"].append(guess)
            game_stat["Bulls"].append(bulls_count)
            game_stat["Cows"].append(cows_count)

            embed = disnake.Embed(title=f"__**Game results:**__", color=0xFFAE00)
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


# @bot.slash_command(name="tic-tac-toe", description="Plays with you in tic-tac-toe game")
# async def play_tic_tac_toe_command(
#         inter: disnake.ApplicationCommandInteraction,
#         difficulty: Literal["easy", "normal", "hard"],
#         mark: Literal["cross", "zero"],
#         player_go_first: Literal["yes", "no"],
# ):
#     field = TicTacToeField()
#     player = TicTacToePlayer(mark=mark, field=field)
#     bot_mark = [arg for arg in get_args(Literal["cross", "zero"]) if arg != mark][0]
#     game_bot = TicTacToeBot(difficulty=difficulty, mark=bot_mark, field=field)
#     game = TicTacToeGame(player_1=player, player_2=game_bot, field=field)


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
        return await inter.channel.send(
            f"Sorry, you took too long. The answer was {answer}."
        )

    if int(guess.content) == answer:
        await inter.channel.send("You guessed correctly!")
    else:
        await inter.channel.send(f"Oops. It is actually {answer}.")


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
    shutil.rmtree(f"{path_to_music}")
    os.mkdir(f"{path_to_music}")


async def user_in_voice_channel(inter: disnake.ApplicationCommandInteraction) -> bool:
    return inter.user.voice is not None


async def bot_is_in_same_channel(inter: disnake.ApplicationCommandInteraction) -> bool:
    return bot.voice_clients[0].channel == inter.user.voice.channel


async def bot_is_in_channel() -> bool:
    return len(bot.voice_clients) != 0


async def bot_is_available_to_connect(
    inter: disnake.ApplicationCommandInteraction,
) -> bool:
    if not await user_in_voice_channel(inter):
        await inter.response.send_message(f"you should be in a voice channel")
        return False
    if await bot_is_in_channel() and not await bot_is_in_same_channel(inter):
        await inter.response.send_message(f"bot sits in another voice channel")
        return False
    return True


async def music_commands_are_available(
    inter: disnake.ApplicationCommandInteraction,
) -> bool:
    if not await bot_is_in_channel():
        await inter.response.send_message(f"bot doesn't sit in any channel")
        return False
    if not await user_in_voice_channel(inter):
        await inter.response.send_message(f"you should be in a voice channel")
        return False
    if not await bot_is_in_same_channel(inter):
        await inter.response.send_message(f"bot sits in another voice channel")
        return False
    return True


@bot.slash_command(name="yam-play", description="Search in yandex music")
async def yam_play_command(
    inter: disnake.ApplicationCommandInteraction,
    _type: Literal["track", "album", "podcast episode", "podcast"],
    name: str,
):
    if not await bot_is_available_to_connect(inter):
        return

    if len(bot.voice_clients) == 0:
        vc = await inter.user.voice.channel.connect(timeout=80)
        await inter.channel.send(f"bot connected to the channel")
    else:
        vc = bot.voice_clients[0]
    bot.music_queue.inter = inter
    bot.music_queue.voice_client = vc

    volume = await yami.YAM().find_by_type(name=name, _type=_type)
    if volume is None:
        return await inter.response.send_message(f"bot couldn't find anything")

    await inter.response.send_message(f"{volume.title} added to queue.")
    await yami.YAM().download(volume=volume)
    await bot.music_queue.add_volume(volume=volume)

    if not vc.is_playing():
        await bot.music_queue.play()


@bot.slash_command(name="pause", description="Pause song")
async def pause_command(inter: disnake.ApplicationCommandInteraction):
    if not await music_commands_are_available(inter):
        return
    if await bot.music_queue.pause():
        await inter.response.send_message(f"music was paused")
    else:
        await inter.response.send_message(f"music is already paused")


@bot.slash_command(name="resume", description="Resume song")
async def resume_command(inter: disnake.ApplicationCommandInteraction):
    if not await music_commands_are_available(inter):
        return
    if await bot.music_queue.resume():
        await inter.response.send_message(f"music was resumed")
    else:
        await inter.response.send_message(f"music is already playing")


@bot.slash_command(name="skip", description="Skip current song")
async def skip_command(
    inter: disnake.ApplicationCommandInteraction,
    to: int = 1,
):
    if not await music_commands_are_available(inter):
        return
    skipped_count = await bot.music_queue.skip(to=to)
    await inter.response.defer()
    await inter.followup.send(
        f"{inter.user.mention} skipped {skipped_count} song{'' if to % 10 == 1 else 's'}"
    )


@bot.slash_command(name="repeat", description="Repeats queue of songs")
async def repeat_command(inter: disnake.ApplicationCommandInteraction):
    if not await music_commands_are_available(inter):
        return
    await bot.music_queue.repeat()
    await inter.response.send_message(f"music was set on repeat")


@bot.slash_command(name="stop", description="Stop playing music")
async def stop_command(inter: disnake.ApplicationCommandInteraction):
    # check if user can use this command
    if not await music_commands_are_available(inter=inter):
        return
    # clean all folders
    await clean_music_folder()
    # stop music queue
    await bot.music_queue.stop()
    await inter.response.send_message(f"bot disconnected from a voice channel")


@bot.slash_command(name="link", description="Returns link on current track")
async def get_link(inter: disnake.ApplicationCommandInteraction):
    if not await music_commands_are_available(inter):
        return
    url = await bot.music_queue.get_url()
    await inter.response.send_message(f"{url}")


@bot.slash_command(name="show_queue", description="Returns queue")
async def get_queue(inter: disnake.ApplicationCommandInteraction):
    if not await music_commands_are_available(inter):
        return
    res = await bot.music_queue.get_list()
    await inter.response.send_message(f"QUEUE")
    for i in range(len(res)):
        await inter.channel.send(f"{i + 1} - {res[i].title}")


YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "False"}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@bot.slash_command(name="youtube-play", description="Search in yandex music")
async def youtube_play_command(
    inter: disnake.ApplicationCommandInteraction, queue: str
):
    if await bot_is_available_to_connect(inter) and inter.guild.voice_client is None:
        vc = await inter.user.voice.channel.connect(timeout=80)
        await inter.channel.send(f"bot connected to the channel")
    else:
        vc = bot.voice_clients[0]

    if vc.is_playing():
        await inter.channel.send(f"bot is already playing a song")
    else:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(queue, download=False)

        url = info["formats"][0]["url"]
        print(url)
        await inter.response.send_message(f"bot is playing [song]({url})")
        vc.play(
            disnake.FFmpegPCMAudio(
                executable="util/ffmpeg", source=url, **FFMPEG_OPTIONS
            )
        )

        while vc.is_playing():
            await asyncio.sleep(1)
        if not vc.is_paused():
            await vc.disconnect(force=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run()
