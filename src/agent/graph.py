from langchain_openai import ChatOpenAI  # 本地私有化部署的大模型
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(
    model='deepseek-chat',
    temperature=0.8,
    api_key='sk-392c92f52e7f4dfb9526ea15d486632e',
    base_url="https://api.deepseek.com",
    extra_body={'chat_template_kwargs': {'enable_thinking': False}},
)


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

graph = create_react_agent(
    llm,
    tools=[get_weather],
    prompt="You are a helpful assistant"
)