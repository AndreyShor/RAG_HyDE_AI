from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
# Point to the local server exposed by LM Studio
# Make sure the server is running in LM Studio!
local_api_base = "http://localhost:1234/v1"
# API key is not needed for local LM Studio server but LangChain requires something
local_api_key = "lm-studio"
# Optional: Specify the model name loaded in LM Studio.
# Often, this isn't strictly necessary as LM Studio serves the loaded model,
# but it can be good practice or required by certain LangChain components.
# You can often find the model identifier in LM Studio.
# If unsure, you can try a placeholder like "local-model".
model_name = "gemma-3-4b-it" # Replace if needed, e.g., "Meta-Llama-3-8B-Instruct-GGUF"

# --- Initialize the LangChain LLM object ---
llm = ChatOpenAI(
    model=model_name,
    openai_api_key=local_api_key,
    openai_api_base=local_api_base,
    temperature=0.7 # Adjust temperature and other parameters as needed
)

print("LLM object configured to use LM Studio server.")

# --- Example Usage (Simple Chain) ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])

output_parser = StrOutputParser()

chain = prompt | llm | output_parser

# --- Run the chain ---
try:
    print("\nSending prompt to local LLM via LangChain...")
    response = chain.invoke({"input": "Explain the difference between Llamas and Alpacas in three sentences."})
    print("\nResponse:")
    print(response)
except Exception as e:
    print(f"\nAn error occurred:")
    print(e)
    print("\nTroubleshooting tips:")
    print("- Is the LM Studio server running?")
    print("- Is the correct model loaded in LM Studio?")
    print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {openai_api_base}")
    print("- Check the LM Studio server logs for errors.")