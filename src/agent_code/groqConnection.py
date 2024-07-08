import os
from dotenv import load_dotenv, find_dotenv
from groq import Groq


class GroqAPIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key is None:
                raise ValueError("API key for Groq is not set in environment variables")
            cls._instance = super(GroqAPIClient, cls).__new__(cls)
            cls._instance.api_key = api_key
            cls._instance.groq = Groq(api_key=api_key)
        return cls._instance.groq

    
