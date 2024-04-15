from .chatbot.controllers.routers import router as chatbot_router
from .conversation.controllers.routers import router as conversation_router

from fastapi import APIRouter


router = APIRouter(prefix='/api/v1')
router.include_router(chatbot_router)
router.include_router(conversation_router)
