import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from aiohttp import web

from .config import config
from .commands import set_commands

from .utils import log

from . import handlers

async def main():
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    if config.custom_bot_api:
        bot.session.api = TelegramAPIServer.from_base(config.custom_bot_api, is_local=True)
    
    if config.bot_fsm_storage == "memory":
        dp = Dispatcher(storage=MemoryStorage())
    else:
        dp = Dispatcher(storage=RedisStorage.from_url(config.redis_dsn))

    dp.include_router(handlers.router)

    await set_commands(bot)
    
    try:
        if not config.webhook_domain:
            log.info('BOT STARTED!')
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        else:
            aiohttp_logger = logging.getLogger("aiohttp.access")
            aiohttp_logger.setLevel(logging.CRITICAL)

            await bot.set_webhook(
                url=config.webhook_domain + config.webhook_path,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )

            app = web.Application()
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.webhook_path)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=config.app_host, port=config.app_port)
            await site.start()
            log.info('BOT STARTED')
            
            await asyncio.Event().wait()
    finally:
        log.info('BOT STOPPED')
        await bot.session.close()