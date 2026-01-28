from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import chat

# print(ChatOpenAI.__init__.__annotations__)
llm = ChatOpenAI(
    model='deepseek-chat',
    temperature=0.8,
    api_key='sk-392c92f52e7f4dfb9526ea15d486632e',
    base_url="https://api.deepseek.com",
    extra_body={'chat_template_kwargs': {'enable_thinking': False}},
)

chatPromot=ChatPromptTemplate.from_messages([
    ("system","你是一个情感专家"),
    ("user","{input}")
])
##json 格式化输出
#outparser=JsonOutputParser()
#output_parser = StrOutputParser()
chain =chatPromot | llm

result=chain.invoke("世界上有爱吗")
print(result)
# messages = [
#     SystemMessage(content="你是一个有帮助的助手"),
#     HumanMessage(content="你好，请介绍你自己")
# ]
# response = chat(messages)
# print(response.content)