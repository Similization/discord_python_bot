import random
from typing import Literal, Any


async def play_rock_paper_scissors(
    move: Literal["rock", "paper", "scissors"]
) -> [Any, str]:
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

    list_of_moves = ["rock", "paper", "scissors"]
    # if move not in list_of_moves:
    #     return await inter.response.send_message(f"You entered wrong word, "
    #                                              f"bot accepts only these words: {list_of_moves}")
    bot_move = random.choice(list_of_moves)
    return bot_move, get_game_result(move, bot_move)
