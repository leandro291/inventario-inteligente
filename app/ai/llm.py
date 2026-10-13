import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    timeout=60,
    max_retries=2,
)

