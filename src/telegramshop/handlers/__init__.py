"""
Пакет обработчиков бота
"""
from aiogram import Router
from . import start, profile, info, shop, admin


def get_handlers_router() -> Router:
    """Получение роутера со всеми обработчиками"""
    router = Router()
    
    router.include_router(start.router)
    router.include_router(admin.router)
    router.include_router(shop.router)
    router.include_router(profile.router)
    router.include_router(info.router)
    
    return router

