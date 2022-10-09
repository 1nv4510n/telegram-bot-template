from aiogram import Router

from .users import default
from .errors import error_handler

router = Router()
router.include_router(default.router)
router.include_router(error_handler.router)