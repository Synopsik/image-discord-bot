import textwrap
import re


async def parse_args(message: str):
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

async def send_message(ctx, message, logger):
   content = message["content"]
   logger.info(f"Message length: {len(content)}")
   
   for chunk in format_text(content):
       await ctx.send(chunk)