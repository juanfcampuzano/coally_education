import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class BaseAgent:
    def __init__(self, template, response_format):
        self.template = template
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key = os.getenv("OPENAI_API_KEY"))
        self.llm = self.llm.bind(response_format=response_format)

    def run(self, inputs):
        prompt = ChatPromptTemplate.from_template(self.template)
        chain = prompt | self.llm
        result = chain.invoke(inputs)

        return result.content