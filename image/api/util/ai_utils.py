from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_aws import ChatBedrock
import os
from dotenv import load_dotenv
load_dotenv()


async def get_llm(name: str, model: str, **kwargs):
    if name == "openai":
        # model = "gpt-4o"
        return ChatOpenAI( 
            model=model, 
            **kwargs
        )
    elif name == "anthropic":
        # model = "claude-3-sonnet-20240620"
        return ChatAnthropic(
            model=model, 
            **kwargs
        )
    elif name == "bedrock":
        # model = "anthropic.claude-3-sonnet-20240229-v1:0"
        return ChatBedrock(
            # credentials_profile_name="bedrock-profile", Might need to readd this
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region="us-east-1",
            model=model, 
            **kwargs
        )
    elif name == "ollama":
        # model = "deepseek-r1:8b"
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        return ChatOllama(
            model=model, 
            temperature=0.7, 
            base_url=ollama_url,
            reasoning=False,
            **kwargs
        )
    else:
        raise ValueError(f"Unknown LLM provider: {name}")
    
    
async def query_llm(query, llm, model, **kwargs):
    inst_llm = await get_llm(llm, model, **kwargs)
    return inst_llm.invoke(query)

