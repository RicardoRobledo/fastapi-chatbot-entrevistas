from typing import List

from ..... import config
from langchain_google_genai import ChatGoogleGenerativeAI


__author__ = 'Ricardo'
__version__ = '0.1'


class GeminiSingleton():


    __client = None


    @classmethod
    def __get_connection(self):
        """
        This method create our client
        """
        
        client = ChatGoogleGenerativeAI(model=config.MODEL, google_api_key=config.GOOGLE_API_KEY)
 
        return client


    def __new__(cls, *args, **kwargs):
        
        #if cls.__client==None:
        cls.__client = cls.__get_connection()

        return cls.__client
    

    @classmethod
    async def post_user_message(cls, text):
        """
        send a message to LLM

        :param text: user message
        """

        msg = await cls.__client.ainvoke(text)

        return msg.content
