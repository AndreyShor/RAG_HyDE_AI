from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from sentence_transformers import SentenceTransformer
from Mongo import MongoDBConnection

from Qdrant import QdrantConnector

import json
import time

import re

from core.logging import SystemLogger


class LLM():

    def __init__(self, model_name: str, local_api_key: str, local_api_base: str):
        self.model_name = model_name
        self.local_api_key = local_api_key
        self.local_api_base = local_api_base

        self.logger = SystemLogger('./logs/basic_log.txt', './logs/rag_log.txt', './logs/hyde_log.txt')

        # Initialize the LangChain LLM object
        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.local_api_key,
            openai_api_base=self.local_api_base,
            temperature=0.7,  # Adjust temperature and other parameters as needed
            max_tokens=10000
        )

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
            start_time = time.time()

            responseAI = chain.invoke({"input": prompt})

            duration = time.time() - start_time

            # Log Creation
            self.logger.log_basic(prompt, responseAI, duration)

            return responseAI
        except Exception as e:
            print(f"\nAn error occurred:")
            print(e)
            print("\nTroubleshooting tips:")
            print("- Is the LM Studio server running?")
            print("- Is the correct model loaded in LM Studio?")
            print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {self.local_api_base}")
            print("- Check the LM Studio server logs for errors.")



    def get_response_as_physics_guru_RAG(self, prompt: str):
        # Define the prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant use your knowledge and additional knowledge provided below to answer question. "),
            ("user", "{input}")
        ])

        startTime_RAG = time.time()

        vectorDb = QdrantConnector()
        topKpapers = vectorDb.similarity_search(prompt, 3)
        context_list = []
        for i, doc in enumerate(topKpapers):
            context_list.append(f"{i}. Description from Knowledge Base which should help you answer the question:\n{doc.payload['text']}\n")

        # Combine the list into a single string
        context = "\n".join(context_list)

        # Build the final prompt context
        promptContext = (
            "There is a list of top 10 documents from the Knowledge Base which should help you to answer the question:\n\n"
            + context
            + "\n"
            + prompt
        )

        duration_RAG = time.time() - startTime_RAG



                # Define the output parser
        output_parser = StrOutputParser()

        chain = prompt_template | self.llm | output_parser

                # Run the chain and get the response
        try:
            print("\nSending prompt to local LLM via LangChain...")
            
            start_time = time.time()

            responseAI = chain.invoke({"input": promptContext})

            durationResponse = time.time() - start_time

            self.logger.log_rag(prompt, context_list, responseAI, durationResponse)

            return responseAI
        except Exception as e:
            print(f"\nAn error occurred:")
            print(e)
            print("\nTroubleshooting tips:")
            print("- Is the LM Studio server running?")
            print("- Is the correct model loaded in LM Studio?")
            print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {self.local_api_base}")
            print("- Check the LM Studio server logs for errors.")


    def get_response_as_physics_guru_HyDE(self, prompt: str):
        # Define the prompt template
        output_parser = StrOutputParser()

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant, DO NOT ASK USER QUESTIONS just answer "),
            ("user", "{input}")
        ])

        query_prep_template = ChatPromptTemplate.from_messages([
            ("system", "DO NOT ASK USER QUESTIONS, just extend user question to assist answering proccess "),
            ("user", "{input}")
        ])

        chainQuery = query_prep_template | self.llm | output_parser

        print("Extension to our prompt: ")

        extendedContext = chainQuery.invoke(prompt)

        extendedPrompt = extendedContext + "\n" + "User prompt: " + prompt

        print(extendedPrompt)


        vectorDb = QdrantConnector()

        topKpapers = vectorDb.similarity_search(extendedPrompt, 3)
        context = ""

        for i, doc in enumerate(topKpapers):
            context += f"{i}. Data \n {doc.payload['text']}\n"

        finalPrompt = context + "\n\n" + extendedPrompt

        print("FinalPrompt: ")

        print(finalPrompt)

        chainMain = prompt_template | self.llm | output_parser

        try:
            print("\nSending prompt to local LLM via LangChain...")
            response = chainMain.invoke({"input": finalPrompt})
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

    def get_repsone_relative_to_person_info_RAG(self, prompt:str, personName): 

        output_parser = StrOutputParser()

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


    def get_repsone_relative_to_person_info_HyDE(self, prompt:str, personName): 

        output_parser = StrOutputParser()


        # Main Agent 
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant of " + personName + "you have access to his data"),
            ("user", "{input}")
        ])

        # Aditional Agent
        query_prep_template = ChatPromptTemplate.from_messages([
            ("system", "You are an agent, your job to extend and clarify user query to guide main agent in short passage"),
            ("user", "{input}")
        ])

        # Get additional instruction
        chainQuery = query_prep_template | self.llm | output_parser
        extendedContext = chainQuery.invoke(prompt)
        agentInstruction = "Helping Agent response: " + extendedContext + "\n \n"

        #  Retrieve User Data
        db = MongoDBConnection()
        userData = db.find_one("profiles", {"_id": personName})
        userData = json.dumps(userData, default=str) 
        userInfo = "There is " + personName + "data about his preferences and life:" + userData


        # Construct final prompt
        finalPrompt = agentInstruction + "\n" + userInfo + "\n" +prompt
        
        print("Finall Prompt")
        print(finalPrompt)
        chain = prompt_template | self.llm | output_parser

                # Run the chain and get the response
        try:
            print("\nSending prompt to local LLM via LangChain...")
            response = chain.invoke({"input": finalPrompt})
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


    def has_self_reference(text: str) -> bool:
        print("test1")
        """Return True if the query contains any 1st-person term."""
        peronn_tag = r"(?i)\b(?:i|me|my|mine|myself|we|us|our|ours|ourselves)\b"
        
        return bool(re.search(peronn_tag, text))

    def has_physics_prefix(text: str) -> bool:
        """Return True if the query starts with 'Phy:' (any casing)."""
        print("text2")
        prefix = re.compile(r"^\s*phy:", re.IGNORECASE)
        return bool(prefix.match(text)) 

        
