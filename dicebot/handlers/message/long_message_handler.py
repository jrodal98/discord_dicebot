#!/usr/bin/env python3

import logging

from dicebot.data.types.message_context import MessageContext
from dicebot.handlers.message.abstract_handler import AbstractHandler
from dicebot.handlers.message.tldrwl_handler import do_tldr_summary

LONG_MESSAGE_CHAR_THRESHOLD = 1000
LONG_MESSAGE_RESPONSE = "https://user-images.githubusercontent.com/2358378/199403413-b1f903f3-998e-481c-9172-8b323cf746f4.png"


class LongMessageHandler(AbstractHandler):
    """Send a funny response for long messages"""

    def __init__(
        self,
        threshold: int = LONG_MESSAGE_CHAR_THRESHOLD,
        skip_image: bool = False,
        autotldr: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.threshold = threshold
        self.skip_image = skip_image
        self.autotldr = autotldr

    async def should_handle(
        self,
        ctx: MessageContext,
    ) -> bool:
        return len(ctx.message.content) > self.threshold

    async def handle(
        self,
        ctx: MessageContext,
    ) -> None:
        logging.info(f"{self.skip_image=}, {self.autotldr=}, {ctx.guild.auto_tldr=}")
        if not self.skip_image:
            await ctx.send(LONG_MESSAGE_RESPONSE)
        if self.autotldr or ctx.guild.auto_tldr:
            summary = await do_tldr_summary(ctx.message.content)
            await ctx.quote_reply(summary)
