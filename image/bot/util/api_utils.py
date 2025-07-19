
async def query(prompt, attachments, logger, show_thoughts=False):
    payload = {
        "query": prompt,
        "attachments": attachments,
        "show_thoughts": show_thoughts
    }
    
    return {
        "response": payload
    }