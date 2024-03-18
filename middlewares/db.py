from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy.ext.asyncio import async_sessionmaker 

class DataBaseSession(BaseMiddleware):
    def __init__(self, session_poll: async_sessionmaker):
        self.session_poll = session_poll

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, any]], Awaitable[any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_poll() as session:
            data["session"] = session
            return await handler(event, data)