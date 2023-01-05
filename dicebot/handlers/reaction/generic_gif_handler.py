#!/usr/bin/env python3

from dicebot.commands import giffer
from dicebot.data.types.message_context import MessageContext
from dicebot.handlers.reaction.abstract_reaction_handler import AbstractReactionHandler


class GenericGifReactionHandler(AbstractReactionHandler):
    def __init__(self) -> None:
        self.triggers = {
            "ok_boomer": "OK boomer",
            "deletethis": "Delete this",
            "press_f": "Press F to pay respects",
            "biden_nice": "Thanks, Obama",
            "cool_dab": "Cool dab",
        }

    @property
    def reaction_name(self) -> str:
        # Not relevant with this handler
        return "_"

    async def should_handle(
        self,
        ctx: MessageContext,
    ) -> bool:
        if not self.meets_threshold_check(ctx):
            return False

        if await self.was_reacted_before(ctx):
            return False

        assert ctx.reaction is not None
        for reaction_name in self.triggers:
            if self.is_emoji_with_name(ctx.reaction, reaction_name):
                return True
        return False

    async def handle(
        self,
        ctx: MessageContext,
    ) -> None:
        # Appease pyright
        assert ctx.reaction is not None
        assert ctx.reactor is not None
        assert not isinstance(ctx.reaction.emoji, str)

        q = self.triggers[ctx.reaction.emoji.name.lower()]
        gif_url = await giffer.get_random_gif_url(q)
        await ctx.channel.send(gif_url, reference=ctx.reaction.message)