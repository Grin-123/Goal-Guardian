# Misc
import os
#from dotenv import load_dotenv
from typing import Optional

# Langchain
from langchain_community.chat_models import ChatOpenAI

# Loading the environmental variables from the containing folder
#load_dotenv(dotenv_path=r'src\\keys\\.env')

# Class creation for openrouter llm connection
class ChatOpenRouter(ChatOpenAI):
    """Class for OpenAI LLMs"""
    openai_api_base: str
    openai_api_key: str
    model_name: str

    def __init__(self,
                model_name: str,
                openai_api_key: Optional[str] = None,
                openai_api_base: str = "https://openrouter.ai/api/v1",
                 **kwargs):
        openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        super().__init__(openai_api_base=openai_api_base,
                        openai_api_key=openai_api_key,
                        model_name=model_name, **kwargs)

class LLMs():
    """Class of LLMs"""
    
    # Free AI Model we will be using 
    mistral = ChatOpenRouter(
    model_name="mistralai/mistral-7b-instruct:free",
    openai_api_key=os.environ.get('OPENAI_API_KEY')
    )

    mythomist = ChatOpenRouter(
    model_name="gryphe/mythomist-7b:free",
    openai_api_key=os.environ.get('OPENAI_API_KEY')
    )
