import textwrap
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)

async def parse_args(message: str) -> Dict[str, str]:
    """ Parse arguments that matches `parameter=variable` """
    pattern = r'(\w+)=([^\s=]+)'
    matches = re.findall(pattern, message)
    return dict(matches)


def format_text(message: str,  max_length: int = 1900) -> list[str]:
    chunks: list[str] = []
    for paragraph in message.split("\n\n"):
        if len(paragraph) <= max_length:
            chunks.append(paragraph)
        else:
            chunks.extend(textwrap.wrap(paragraph,
                                        width=max_length,
                                        break_long_words=False,
                                        break_on_hyphens=False))
    return chunks

async def send_message(ctx, message):
   for chunk in format_text(message["content"]):
       await ctx.send(chunk)