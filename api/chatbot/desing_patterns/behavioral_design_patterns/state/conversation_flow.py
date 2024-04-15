from .states import InitialState
from . import states


__author__ = 'Ricardo'
__version__ = '0.1'


class ConversationFlow():
    """
    This class is define our conversation flow based in the behavioral design pattern 'state'
    """


    def __init__(self, state=None):

        self.__actual_state = None

        if not state=='inicio':
            self.__actual_state = states.get_states()[state]
        else:
            self.__actual_state = InitialState()
    

    #def get_state_number_parameters(self):
    #    import inspect
    #    return len(inspect.signature(self.__actual_state.send_message).parameters)


    async def send_message(self, conversational_id, state, text, conversation):
        
        # send message
        msg = await self.__actual_state.send_message(conversational_id, state, text, conversation)

        return msg
