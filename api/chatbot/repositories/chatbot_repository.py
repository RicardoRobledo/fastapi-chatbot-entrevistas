from ..desing_patterns.behavioral_design_patterns.state.conversation_flow import ConversationFlow


class ChatbotRepository():

    async def post_user_message(self, conversational_id, state, message, conversation):
        
        conversation_flow = ConversationFlow(state)
        msg = await conversation_flow.send_message(conversational_id, state, message, conversation)

        return msg
