import aiosqlite
import sqlite3
import logging
import asyncio
import uuid

from rebelykos.core.utils import get_path_in_data_folder


class AsyncRLDatabase:
    def __init__(self, db_path=get_path_in_data_folder("rl.db")):
        self.db_path = db_path

    @staticmethod
    async def create_db_and_schema(db_path=get_path_in_data_folder("rl.db")):
        async with aiosqlite.connect(db_path) as db:
            await db.execute('''CREATE TABLE "profiles" (
                "id" integer PRIMARY KEY,
                "profile" text,
                "access_key_id" text,
                "secret_access_key" text,
                "region" text,
                UNIQUE(profile)
            )''')
