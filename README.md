# Discord bot for personal usage

## What can he do?
1. slash-commands
   1. **/ping**\
   __description:\
   Will check if bot is online.\
   __return:\
   ***@user, pong!***
   2. **/roll** *_from: int = 1*, *_to: int = 6*\
   __description:\
   Will get a random number.\
   __return:\
   ***@user, rolled {random_number}!***
   3. **/rock-paper-scissors** *move: Literal["rock", "paper", "scissors"]*\
   __description:\
   Will play with you in rock paper scissors game.\
   __return:\
   ***@user, played {your_move}!***\
   ***bot played {bot_move}***\
   ***{game_result}***
   4. **/bulls-and-cows**\
   __description:\
   Will play with you in bulls and cows game, 
   bot will listen to all of your messages and reacts only when you type a 4 digits number,
   he will update his previous message with all results of your previous guesses.\
   __return:
      * ***You win, the number is: {generated_number}, it took you {count_of_tries} moves*** - if you guessed correct
      * ***Sorry, you took too long. The answer was {answer}.*** - if you waited too long
   5. **/guess-number** *_from: int = 1*, *_to: int = 10*\
   __description:\
   Will play with you in guess number game.
   __return:
      * ***You guessed correctly!***                             - if you guessed right
      * ***Oops. It is actually {answer}.***                     - if you didn't guess
      * ***Sorry, you took too long. The answer was {answer}.*** - if you waited too long
   6. **/balaboba** *text: str*, *language: Literal["en" ,"ru"] = "ru"*\
   __description:\
   Will use balaboba to generate you a random text.\
   __return:
      * ***You guessed correctly!***                             - if you guessed right
      * ***Oops. It is actually {answer}.***                     - if you didn't guess
      * ***Sorry, you took too long. The answer was {answer}.*** - if you waited too long
   7. **yam-commands**\
   __description:\
   Will appear in the future.
2. Will appear in the future.

