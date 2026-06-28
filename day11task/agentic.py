from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
 
# Load .env
load_dotenv(override=True)
 
# Create LLM
llm = ChatAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model=os.getenv("LLM_MODEL"),
    base_url=os.getenv("LLM_ENDPOINT"),
    temperature=1.0,
    max_tokens=4096,
    streaming=False
)
 
# Ask a question
response = llm.invoke("What is Agentic AI?")
 
print(response.content)