from fastapi import APIRouter
from ... import config

import pymongo


router = APIRouter(prefix='/conversation', tags=['Conversation'])

@router.post('')
async def create_conversation():

    connection = pymongo.MongoClient(f'mongodb+srv://{config.USERNAME}:{config.PASSWORD}@entrevista.eiea1bs.mongodb.net/?retryWrites=true&w=majority&appName=Entrevista')

    db = connection['sample_mflix']
    collection = db['users']

    documento = {
        "data": {
            "state": "inicio",
            "conversation": []
        },
    }

    data = collection.insert_one(documento)
    connection.close()
    return {'conversational_id': str(data.inserted_id)}


@router.post('/cleaner-manager')
async def delete_conversation():
    return {'message': 'deleted'}
