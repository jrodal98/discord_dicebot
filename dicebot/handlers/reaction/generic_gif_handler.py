#!/usr/bin/env python3

import datetime
import logging
import string

from dicebot.commands import giffer
from dicebot.data.types.message_context import MessageContext
from dicebot.handlers.reaction.abstract_reaction_handler import AbstractReactionHandler


class GenericGifReactionHandler(AbstractReactionHandler):
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
            logging.warning("New reaction on message but it was reacted before.")
            return False

        assert ctx.reaction is not None
        # Check this server's custom reactions
        handlers = await ctx.guild.get_all_reaction_handlers(ctx.session)
        for handler in handlers:
            if handler.reaction_equal(ctx.reaction):
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

        logging.info(f"Calling handle for reaction {ctx.reaction}")

        # Check if this was *really* funny
        current_date = datetime.datetime.now()
        now = current_date.replace(tzinfo=datetime.timezone.utc)
        elapsed = now - ctx.reaction.message.created_at
        is_turbo = elapsed.total_seconds() <= ctx.guild.turbo_reaction_threshold

        # This is kind of hard-coding specific behavior for our server...
        # But... it's my bot. So I don't care.
        # If the reaction was this_tbh and the message began with hbd, send a birthday
        # gif instead of the server's custom handler.
        is_this_tbh = ctx.reaction.emoji.name.upper() == "THIS_TBH" 
        is_hbd = ctx.message.content.upper().startswith("HBD")
        if is_this_tbh and is_hbd:
            logging.info("Short-circuiting for hbd gif")
            gif_url = await giffer.get_random_gif_url("grumpy birthday")
            if gif_url is not None:
                await ctx.quote_reply(gif_url)
            # Regardless of whether we sent a quote reply, return here
            # because otherwise we may get an IndexError below for a bad lookup.
            return


        if is_turbo:
            emojis = {e.name: f"<:{e.name}:{e.id}>" for e in ctx.client.emojis}
            turbo = ["T_", "U_", "R_", "B_", "O_"]
            turbo_str = "".join(emojis[s] for s in turbo)
            name = [f"{char}_" for char in ctx.reaction.emoji.name.upper()]
            name_str = "".join(
                emojis[s] for s in name if s[0] in string.ascii_uppercase
            )
            turbo_msg = f"{turbo_str} {name_str}"
            await ctx.quote_reply(turbo_msg, silent=False)

        # Check this server's custom reactions
        handlers = await ctx.guild.get_all_reaction_handlers(ctx.session)
        for handler in handlers:
            if handler.reaction_equal(ctx.reaction):
                logging.info(
                    f"Using custom logic for {ctx.reaction}: {handler.gif_search}"
                )
                gif_url = await giffer.get_random_gif_url(handler.gif_search)
                if gif_url is not None:
                    await ctx.quote_reply(gif_url)
                # Regardless of whether we sent a quote reply, return here
                # because otherwise we may get an IndexError below for a bad lookup.
                return
