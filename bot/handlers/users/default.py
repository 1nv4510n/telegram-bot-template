import asyncio
import random

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Text

router = Router()

@router.message(Command('start'))
async def start_command_handler(message: Message) -> None:
    await message.answer('Hello, world!')