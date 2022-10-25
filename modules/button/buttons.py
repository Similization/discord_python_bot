import disnake
from discord.ui import Button, View
from disnake import ButtonStyle


class BlurpleButton(Button):
    def __init__(self, label, emoji=None):
        super().__init__(label=label, style=ButtonStyle.blurple, emoji=emoji)


class CustomView(View):
    def __init__(self, member: disnake.Member):
        self.member = member
        super().__init__(timeout=180)

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        if inter.author != self.member:
            await inter.response.send_message(
                content="You don't have permission to press this button.",
                ephemeral=True,
            )
            return False
        return True
