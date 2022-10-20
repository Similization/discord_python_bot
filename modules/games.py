import random

from typing import Literal


class Games:
    def __init__(self):
        pass

    @staticmethod
    async def play_rock_paper_scissors(move: Literal['rock', 'paper', 'scissors']) -> str:
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
        return get_game_result(move, bot_move)

    async def play_bulls_and_cows(self, guess):
        def generate_number_for_bulls_and_cows_game():
            all_numbers = [str(x) for x in range(10)]
            result = ''.join(random.sample(all_numbers, 4))
            # for i in range(4):
            #     number = random.choice(all_numbers)
            #     result += number
            #     all_numbers.remove(number)
            return result

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

        answer = generate_number_for_bulls_and_cows_game()

        return compare_guess_and_answer(answer, guess)


class TicTacToe:
    def __init__(self, difficulty: Literal["easy", "normal", "hard"]):
        self.difficult = difficulty
        self.fields = ['' for i in range(9)]

    def is_field_empty(self):
        return len(''.join(self.fields)) == 0

    def is_field_full(self):
        return len(''.join(self.fields)) == 9

    def start_game(self):
        pass
