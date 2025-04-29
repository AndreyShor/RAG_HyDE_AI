import json
import time
import re

from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from DB.Mongo import MongoDBConnection
from DB.Qdrant import QdrantConnector

from core.logging import SystemLogger


class LLM():

    def __init__(self, model_name: str, local_api_key: str, local_api_base: str):
        self.model_name = model_name
        self.local_api_key = local_api_key
        self.local_api_base = local_api_base

        self.logger = SystemLogger('./logs/basic_log.txt', './logs/rag_log.txt', './logs/hyde_log.txt')

        # Initialize the LangChain LLM object
        self.llm = ChatOpenAI(
            model=self.model_name, # type: ignore
            openai_api_key=self.local_api_key, # type: ignore
            openai_api_base=self.local_api_base, # type: ignore
            temperature=0.7,  # Adjust temperature and other parameters as needed
            max_tokens=10000 # type: ignore
        )

    def get_response_normal(self, prompt: str):
        """This function is used to get the response from the LLM without any additional context or RAG."""

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
        """This function is used to get the response from the LLM with RAG (Retrieval-Augmented Generation) on Physics Data Set."""
        
        # Define the prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant use your knowledge and additional knowledge provided below to answer question. "),
            ("user", "{input}")
        ])

        startTime_RAG = time.time()

        vectorDb = QdrantConnector()
        topKpapers = vectorDb.similarity_search(prompt, 3)

        context_list: List[str] = []

        for i, doc in enumerate(topKpapers):
            raw_text = doc.payload['text']  # type: ignore
            formatted_text = self._format_text(raw_text)  # Format each doc
            context_list.append(
                f"{i}. Description from Knowledge Base which should help you answer the question:\n{formatted_text}\n"
            )

        # Combine the list into a single string
        contextDocs = "\n".join(context_list)

        # Build the final prompt context
        promptContext = (
            "There is a list of top 10 documents from the Knowledge Base which should help you to answer the question:\n\n"
            + contextDocs
            + "\n User prompt to answer:\n"
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

            self.logger.log_rag(prompt, context_list, responseAI, durationResponse, duration_RAG) # type: ignore

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
        """This function is used to get the response from the LLM with HyDE (Hypothetical Document Embeddings) on Physics Data Set."""

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

        start_time = time.time()
        agentResponse = chainQuery.invoke(prompt) # type: ignore
        durationAgent = time.time() - start_time

        extendedPrompt = "Use agent suggestion to give resposne: " + agentResponse + "\n" + "User prompt to asnwer: " + prompt


        start_time = time.time()
        vectorDb = QdrantConnector()
        topKpapers = vectorDb.similarity_search(extendedPrompt, 3)

        context_list: List[str] = []

        for i, doc in enumerate(topKpapers):
            raw_text = doc.payload['text']  # type: ignore
            formatted_text = self._format_text(raw_text)  # Format each doc
            context_list.append(
                f"{i}. Description from Knowledge Base which should help you answer the question:\n{formatted_text}\n"
            )

        # Combine the list into a single string
        contextDocs = "\n".join(context_list)
        durationRAG = time.time() - start_time

        # Build the final prompt context
        finalPrompt = (
            "There is a list of top 10 documents from the Knowledge Base which should assist you to answer the question:\n\n"
            + contextDocs
            + "\n"
            + extendedPrompt
        )


        chainMain = prompt_template | self.llm | output_parser

        try:
            print("\nSending prompt to local LLM via LangChain...")
            start_time = time.time()
            response = chainMain.invoke({"input": finalPrompt})
            durationResponse = time.time() - start_time
            
            self.logger.log_hyde(prompt, agentResponse, context_list, response, durationResponse, durationRAG, durationAgent) # type: ignore

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
        """This function is used to get the response from the LLM with RAG (Retrieval-Augmented Generation) on User Personal Data Set."""
        
        output_parser = StrOutputParser()

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("user", "{input}")
        ])

        start_time = time.time()

        db = MongoDBConnection()
        userData = db.find_one("profiles", {"_id": personName})
        userData = json.dumps(userData, default=str) 
        durationRAG = time.time() - start_time
        context = "You are given user profile. Dont tell user anything about his profile at all just answer his quesion without any aditional questions " + userData

        promptContext = context + "\n" + prompt


        chain = prompt_template | self.llm | output_parser

                # Run the chain and get the response
        try:
            print("\nSending prompt to local LLM via LangChain...")

            start_time = time.time()
            response = chain.invoke({"input": promptContext})
            durationResponse = time.time() - start_time

            self.logger.log_rag(prompt, context, response, durationResponse, durationRAG) # type: ignore

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
        """This function is used to get the response from the LLM with HyDE (Hypothetical Document Embeddings) on User Personal Data Set."""
        
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
        start_time = time.time()
        chainQuery = query_prep_template | self.llm | output_parser
        extendedContext = chainQuery.invoke(prompt) # type: ignore
        durationAgent = time.time() - start_time
        agentInstruction = "Helping Agent response: " + extendedContext + "\n \n"

        #  Retrieve User Data
        start_time = time.time()
        db = MongoDBConnection()
        userData = db.find_one("profiles", {"_id": personName})
        userData = json.dumps(userData, default=str) 
        userInfo = "There is " + personName + "data about his preferences and life:" + userData
        durationRAG = time.time() - start_time

        # Construct final prompt
        finalPrompt = agentInstruction + "\n" + userInfo + "\n" +prompt
        
        chain = prompt_template | self.llm | output_parser

                # Run the chain and get the response
        try:
            print("\nSending prompt to local LLM via LangChain...")
            start_time = time.time()
            response = chain.invoke({"input": finalPrompt})
            durationResponse = time.time() - start_time

            # Log Creation
            self.logger.log_hyde(prompt, agentInstruction, userInfo, response, durationResponse, durationRAG, durationAgent) # type: ignore
            return response
        except Exception as e:
            print(f"\nAn error occurred:")
            print(e)
            print("\nTroubleshooting tips:")
            print("- Is the LM Studio server running?")
            print("- Is the correct model loaded in LM Studio?")
            print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {self.local_api_base}")
            print("- Check the LM Studio server logs for errors.")

    def has_self_reference(self, text: str) -> bool:
        """Return True if the query contains any 1st-person term."""

        peronn_tag = r"(?i)\b(?:i|me|my|mine|myself|we|us|our|ours|ourselves)\b"
        
        return bool(re.search(peronn_tag, text))

    def has_physics_prefix(self, text: str) -> bool:
        """Return True if the query starts with 'Phy:' (any casing)."""

        prefix = re.compile(r"^\s*phy:", re.IGNORECASE)
        return bool(prefix.match(text)) 
    
    def _format_text(self, text: str, max_length: int = 500) -> str:
        """Format the text to fit within the specified maximum length."""

        text = text.replace('\n', ' ').strip()
        words = text.split()
        lines = []
        line = ''
        for word in words:
            if len(line) + len(word) + 1 <= max_length:
                line += (' ' if line else '') + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return '\n'.join(lines)

        
