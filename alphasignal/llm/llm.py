import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_mistralai.chat_models import ChatMistralAI


class LLM:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER")
        self.llm = self._get_llm()

    def _get_llm(self):
        if self.llm_provider == "openai":
            llm = ChatOpenAI(
                model=os.getenv("OPENAI_LLM_MODEL"), api_key=os.getenv("OPENAI_API_KEY")
            )
        elif self.llm_provider == "anthropic":
            llm = ChatAnthropic(
                model=os.getenv("ANTHROPIC_LLM_MODEL"),
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        elif self.llm_provider == "google":
            llm = ChatGoogleGenerativeAI(
                model=os.getenv("GOOGLE_LLM_MODEL"), api_key=os.getenv("GOOGLE_API_KEY")
            )
        elif self.llm_provider == "deepseek":
            llm = ChatDeepSeek(
                model=os.getenv("DEEPSEEK_LLM_MODEL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
            )
        elif self.llm_provider == "mistral":
            llm = ChatMistralAI(
                model=os.getenv("MISTRAL_LLM_MODEL"),
                api_key=os.getenv("MISTRAL_API_KEY"),
            )
        else:
            raise ValueError("Invalid LLM provider")
        return llm
