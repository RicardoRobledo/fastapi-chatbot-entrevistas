from ..repositories.chatbot_repository import ChatbotRepository 


class ChatbotService():

    async def post_user_message(self, conversational_id, state, message, conversation):

        return await ChatbotRepository().post_user_message(conversational_id, state, message, conversation)
