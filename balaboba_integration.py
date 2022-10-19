import asyncio

from aiobalaboba import Balaboba
from typing import Literal


async def generate_text(text: str, language: Literal["en", "ru"]):
    bb = Balaboba()

    # Get text types
    intros = await bb.intros(language=language)

    # Get the first text type
    intro = next(intros)

    # Print Balaboba's response to the "Hello" query
    response = await bb.balaboba(text, intro=intro.number)
    return response


# asyncio.run(generate_text("tree was very high and beautiful", "en"))
