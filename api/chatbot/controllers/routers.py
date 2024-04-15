from fastapi import APIRouter, Request

from ..services.chatbot_service import ChatbotService
from ... import config

import pymongo
import urllib


connection = pymongo.MongoClient(f'mongodb+srv://{config.USERNAME}:{config.PASSWORD}@entrevista.eiea1bs.mongodb.net/?retryWrites=true&w=majority&appName=Entrevista')


router = APIRouter(prefix='/chatbot/msg', tags=['Chatbot'])

@router.post('')
async def get_users(request:Request):

    global connection

    db = connection['sample_mflix']
    collection = db['users']

    metodo = request.method
    
    # Obtener la URL completa de la solicitud
    url = str(request.url)
    
    # Obtener los parámetros de consulta de la solicitud
    parametros_query = request.query_params
    
    # Obtener los datos del cuerpo de la solicitud (si los hay)
    datos_cuerpo = await request.body()
    datos_json = datos_cuerpo.decode("utf-8")
    datos_decodificados = urllib.parse.parse_qs(datos_json)

    conversational_id = datos_decodificados['conversational_id'][0]
    message = datos_decodificados['message'][0]
    print(message)

    # Obtener las cabeceras de la solicitud
    cabeceras = request.headers
    
    # Obtener la dirección IP del cliente que realizó la solicitud
    direccion_ip_cliente = request.client.host
    
    # Puedes imprimir o hacer lo que necesites con esta información
    #print("Método:", metodo)
    #print("URL:", url)
    #print("Parámetros de consulta:", parametros_query)
    #print("Datos del cuerpo:", datos_cuerpo)
    #print("Cabeceras:", cabeceras)
    #print("Dirección IP del cliente:", direccion_ip_cliente)

    from bson.objectid import ObjectId

    import asyncio
    loop = asyncio.get_event_loop()
    data = (await loop.run_in_executor(None, collection.find_one, {'_id':ObjectId(conversational_id)}, {'_id':0, 'data':1}))['data']
    #data = await collection.find_one({'_id':ObjectId(conversational_id)}, {'_id':0, 'data':1})['data']

    msg = await ChatbotService().post_user_message(conversational_id, data['state'], message, conversational_id)

    return {'msg':msg}
