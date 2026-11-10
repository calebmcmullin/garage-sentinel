import asyncio
from db.database import delete_expired_registrations

EXPIRATION_MINUTES = 10

async def registration_cleanup_tool():
    while True:
        await delete_expired_registrations(EXPIRATION_MINUTES)
        await asyncio.sleep(1)