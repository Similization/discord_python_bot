import random


class BullsAndCows:
    def __init__(self):
        self.answer = self.generate_number_for_bulls_and_cows_game()

    @staticmethod
    def generate_number_for_bulls_and_cows_game():
        all_numbers = [str(x) for x in range(10)]
        result = "".join(random.sample(all_numbers, 4))
        # for i in range(4):
        #     number = random.choice(all_numbers)
        #     result += number
        #     all_numbers.remove(number)
        return result

    async def compare_guess_and_answer(self, _guess: str):
        _bulls_count = 0
        _cows_count = 0
        for i in range(4):
            # find pos of guess[i] symbol in answer
            pos = self.answer.find(_guess[i])
            # has symbol and it has same position
            if pos == i:
                _bulls_count += 1
            # has symbol, but its position is different
            elif pos != -1:
                _cows_count += 1
        return _bulls_count, _cows_count
