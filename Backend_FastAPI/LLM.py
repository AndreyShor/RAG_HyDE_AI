from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from sentence_transformers import SentenceTransformer
from Mongo import MongoDBConnection

from Qdrant import QdrantConnector

import json


class LLM():

    def __init__(self, model_name: str, local_api_key: str, local_api_base: str):
        self.model_name = model_name
        self.local_api_key = local_api_key
        self.local_api_base = local_api_base

        # Initialize the LangChain LLM object
        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.local_api_key,
            openai_api_base=self.local_api_base,
            temperature=0.7  # Adjust temperature and other parameters as needed
        )

        print("LLM object configured to use LM Studio server.")


    def get_response_normal(self, prompt: str):
        # Define the prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("user", "{input}")
        ])

        # Define the output parser
        output_parser = StrOutputParser()

        # Create the chain
        chain = prompt_template | self.llm | output_parser

        # Run the chain and get the response
        try:
            print("\nSending prompt to local LLM via LangChain...")
            response = chain.invoke({"input": prompt})
            print("\nResponse:")
            print(response)
            return response
        except Exception as e:
            print(f"\nAn error occurred:")
            print(e)
            print("\nTroubleshooting tips:")
            print("- Is the LM Studio server running?")
            print("- Is the correct model loaded in LM Studio?")
            print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {self.local_api_base}")
            print("- Check the LM Studio server logs for errors.")



    def get_response_as_physics_guru(self, prompt: str):
        # Define the prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant use your knowledge and additional knowledge provided below to answer question. "),
            ("user", "{input}")
        ])

        print(f"Prompt before adding documents: {prompt}")

        vectorDb = QdrantConnector()

        topKpapers = vectorDb.similarity_search(prompt, 3)
        context = ""

        for i, doc in enumerate(topKpapers):
            context += f"{i}. Description from Knowledge base which should help you to answer question \n {doc.payload['text']}\n"

        prompt = "There is a list of top 10 documents from knowledgebase which should help you to answer the question \n " + context + "\n" + prompt


        print(prompt)

                # Define the output parser
        output_parser = StrOutputParser()

        chain = prompt_template | self.llm | output_parser

                # Run the chain and get the response
        try:
            print("\nSending prompt to local LLM via LangChain...")
            response = chain.invoke({"input": prompt})
            print("\nResponse:")
            print(response)
            return response
        except Exception as e:
            print(f"\nAn error occurred:")
            print(e)
            print("\nTroubleshooting tips:")
            print("- Is the LM Studio server running?")
            print("- Is the correct model loaded in LM Studio?")
            print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {self.local_api_base}")
            print("- Check the LM Studio server logs for errors.")


    def get_repsone_relative_to_person_info(self, prompt:str, personName): 
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("user", "{input}")
        ])

        print("Name: " + personName)

        db = MongoDBConnection()
        userData = db.find_one("profiles", {"_id": personName})

        userData = json.dumps(userData, default=str) 

        print(userData)

        context = "You are given user profile. Dont tell user anything about his profile at all just answer his quesion without any aditional questions " + userData

        prompt = prompt + context

        output_parser = StrOutputParser()

        chain = prompt_template | self.llm | output_parser

                # Run the chain and get the response
        try:
            print("\nSending prompt to local LLM via LangChain...")
            response = chain.invoke({"input": prompt})
            print("\nResponse:")
            print(response)
            return response
        except Exception as e:
            print(f"\nAn error occurred:")
            print(e)
            print("\nTroubleshooting tips:")
            print("- Is the LM Studio server running?")
            print("- Is the correct model loaded in LM Studio?")
            print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {self.local_api_base}")
            print("- Check the LM Studio server logs for errors.")







        
