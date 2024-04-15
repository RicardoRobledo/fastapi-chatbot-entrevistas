from abc import ABC, abstractmethod

import pandas as pd
import inspect
from . import states

from ..... import config 
from ...creational_patterns.singleton.gemini_singleton import GeminiSingleton


__author__ = 'Ricardo'
__version__ = '0.1'


__all__ = ['InitialState', 'EvaluationQuestionState']



def load_prompt_file(prompt_file_path:str):

    prompt_file_path = prompt_file_path
    template = ''

    with open(prompt_file_path, 'r', encoding="utf-8") as archivo:
        template = archivo.read()

    return template


class BaseState(ABC):

    @abstractmethod
    def send_message(self, text, conversation):
        pass


class InitialState(BaseState):
    """
    This class define the first state
    """


    def __init__(self):
        self.__name = 'inicio'
        self.__next = 'evaluation_question'

    
    @property
    def name(self):
        return self.__name


    async def send_message(self, conversational_id, state, text, conversation):
        """
        sens a message loading the initial prompt file to send
        
        :param text: message to send
        :param conversation: history of the conversation
        :return: tuple with the name of the state and the message
        """


        initial_prompt = load_prompt_file('api/chatbot/prompts/initial_prompt.txt')
        msg = await GeminiSingleton.post_user_message(initial_prompt.format(
            tema="Marketing",
            vacante="""
            Descripción del puesto:

            Buscamos un administrador de empresas con experiencia para unirse a nuestro equipo y desempeñar un papel fundamental en el éxito de nuestra empresa.

            Responsabilidades:

            Planificación estratégica: Desarrollar e implementar planes estratégicos para el crecimiento y la rentabilidad de la empresa.
            Gestión financiera: Supervisar la elaboración del presupuesto, controlar los gastos y optimizar el flujo de caja.
            Recursos humanos: Gestionar el talento humano, incluyendo la contratación, selección, formación y desarrollo del personal.
            Operaciones: Dirigir las operaciones diarias de la empresa, asegurando la eficiencia y productividad.
            Liderazgo: Inspirar y motivar al equipo, creando un ambiente de trabajo positivo y productivo.
            Toma de decisiones: Tomar decisiones estratégicas y operativas basadas en datos y análisis.
            Comunicación: Comunicarse de manera efectiva con los empleados, clientes, proveedores y otros stakeholders.
            Requisitos:

            Licenciatura en Administración de Empresas o carrera afín.
            Experiencia mínima de 5 años en un puesto de gestión.
            Excelentes habilidades de liderazgo, comunicación y toma de decisiones.
            Capacidad para trabajar de forma independiente y como parte de un equipo.
            Orientación a resultados y capacidad para cumplir objetivos.
            Dominio de herramientas informáticas (Microsoft Office, Excel, etc.).
            Se valorará:

            Experiencia en la industria específica.
            Habilidades en análisis financiero y contable.
            Conocimiento de idiomas (inglés, etc.).
            Certificaciones o cursos relevantes.
            """
            ))
        
        import ast
        questions = ast.literal_eval(msg)

        df = pd.DataFrame({'Questions': questions})
        df.to_csv('api/questions.csv', index=False)

        import pymongo

        connection = pymongo.MongoClient(f'mongodb+srv://{config.USERNAME}:{config.PASSWORD}@entrevista.eiea1bs.mongodb.net/?retryWrites=true&w=majority&appName=Entrevista')
        db = connection['sample_mflix']
        collection = db['users']

        from bson.objectid import ObjectId

        #collection.update_one({'_id':ObjectId(conversational_id)}, {'$set': {'data.state': self.__next}})
        import asyncio
        loop = asyncio.get_event_loop()
        filtro = {'_id': ObjectId(conversational_id)}
        actualizacion = {'$set': {'data.state': self.__next}}
        resultado = await loop.run_in_executor(None, collection.update_one, filtro, actualizacion)

        return df.iloc[0, 0]


class EvaluationQuestionState(BaseState):
    """
    This class evaluate the user
    """


    def __init__(self):
        self.__name = 'evaluation_question'
        self.__next = self.__name

    
    @property
    def name(self):
        return self.__name


    async def send_message(self, conversational_id, state, message, conversation):

        df = pd.read_csv('api/questions.csv')

        initial_prompt = load_prompt_file('api/chatbot/prompts/prompt.txt')
        preg = df.iloc[0, 0]
        msg = await GeminiSingleton.post_user_message(
            initial_prompt.format(pregunta=preg, respuesta=message)
        )

        import ast
        answer = ast.literal_eval(msg)

        import pymongo

        connection = pymongo.MongoClient(f'mongodb+srv://{config.USERNAME}:{config.PASSWORD}@entrevista.eiea1bs.mongodb.net/?retryWrites=true&w=majority&appName=Entrevista')
        db = connection['sample_mflix']
        collection = db['users']

        from bson.objectid import ObjectId

        respuesta = answer[0]
        calificacion = answer[1]

        data = {'pregunta':preg, 'respuesta':message, 'evaluacion':respuesta, 'calificacion':calificacion}
            
        #collection.find_one({'_id':ObjectId(conversational_id)}, {'_id':0, 'data.conversation':1})
        
        collection.update_one(
            {'_id':ObjectId(conversational_id)},
            {
                '$set': {'data.state': self.__next},
                '$push':{'data.conversation': data},
            })
    
        df = pd.read_csv('api/questions.csv')
        df = df.drop(0)
        df.to_csv('api/questions.csv', index=False)

        if len(df)>0:

            return f'Siguiente pregunta: {df.iloc[0, 0]}'

        else:

            self.__next = 'end'

            import pymongo

            connection = pymongo.MongoClient(f'mongodb+srv://{config.USERNAME}:{config.PASSWORD}@entrevista.eiea1bs.mongodb.net/?retryWrites=true&w=majority&appName=Entrevista')
            collection = db['users']

            from bson.objectid import ObjectId
            
            #collection.find_one({'_id':ObjectId(conversational_id)}, {'_id':0, 'data.conversation':1})
        
            collection.update_one(
                {'_id':ObjectId(conversational_id)},
                {
                    '$set': {'data.state': self.__next},
                })

            return await EndState().send_message(conversational_id, state, message, conversation)


class EndState(BaseState):
    """
    This class evaluate the user
    """


    def __init__(self):
        self.__name = 'end'

    
    @property
    def name(self):
        return self.__name


    async def send_message(self, conversational_id, state, message, conversation):

        msg = 'Tu sesion de entrevista ha terminado, gracias por tu tiempo \U0001F642.'
        return msg


def get_states():
    

    states = {}
    global_variables = globals()

    for class_name, class_value in global_variables.items():

        if (inspect.isclass(class_value)
            and not inspect.isabstract(class_value)
            and class_value.__module__ == __name__):

            class_obj = class_value()
            states[class_obj.name] = class_obj
    
    return states
