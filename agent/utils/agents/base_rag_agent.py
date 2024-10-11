import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pymongo import MongoClient
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.runnables import RunnablePassthrough
from youtube_search import YoutubeSearch

class BaseRagAgent:
    def __init__(self, template, response_format):
        self.template = template
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key = os.getenv("OPENAI_API_KEY"))
        self.llm = self.llm.bind(response_format=response_format)

        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.collection = self.client[os.getenv("EMBEDDINGS_DB_NAME")][os.getenv("EMBEDDINGS_COLLECION_NAME")]
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.vectorStore = MongoDBAtlasVectorSearch( self.collection, self.embeddings )



    def run(self, inputs):
        
        retriever = self.vectorStore.as_retriever()

        def format_docs(topics):
            result = {}
            for topic in topics:
                docs = retriever.get_relevant_documents(topic, k=1)
                
                if topic not in result:
                    result[topic] = []

                for doc in docs:
                    result[topic].append({
                        "text": doc.page_content,
                        "titulo": doc.metadata.get("titulo", "Sin título"),
                        "url": doc.metadata.get("url", "Sin URL")
                    })
                
                youtube_results = YoutubeSearch('curso de ' + topic, max_results=2).to_dict()
                for video in youtube_results:
                    result[topic].append({
                        "text": video['title'],
                        "titulo": video['title'],
                        "url": 'https://www.youtube.com' + video['url_suffix']
                    })
            
            return result

        inputs['context'] = format_docs(inputs['topics'])
        prompt = ChatPromptTemplate.from_template(self.template)
        chain = (
            prompt | self.llm)
        result = chain.invoke(inputs)

        return result.content