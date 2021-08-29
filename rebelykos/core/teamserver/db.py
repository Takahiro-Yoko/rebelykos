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
                "session_token" text,
                UNIQUE(profile)
            )''')

    async def add_profile(self, profile, access_key_id,
                          secret_access_key, region):
        await self.db.execute("INSERT INTO profiles (profile, "
                              "access_key_id, secret_access_key, region) "
                              "VALUES (?,?,?,?)",
                              [profile, access_key_id,
                               secret_access_key, region])

    async def get_profiles(self):
        async with self.db.execute("SELECT * FROM profiles") as cursor:
            async for row in cursor:
                yield row

    async def __aenter__(self):
        self.db = await aiosqlite.connect(self.db_path)
        return self

    async def __aexit__(self, exec_type, exc, tb):
        await self.db.commit()
        await self.db.close()

class RLDatabase:

    def __init__(self, db_path=get_path_in_data_folder("rl.db")):
        self.db_path = db_path

    def get_profiles(self):
        with self.db:
            for row in self.db.execute("SELECT * from profiles").fetchall():
                yield row

    def upsert(self, data):
        with self.db:
            self.db.execute(
                "INSERT OR REPLACE INTO profiles (profile, access_key_id,"
                "                                 secret_access_key, region,"
                "                                 session_token)"
                "    VALUES (?, ?, ?, ?, ?)",
                [data[k] for k in ("profile", "access_key_id",
                                   "secret_access_key", "region",
                                   "session_token")]
            )

    def __enter__(self):
        self.db = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, exec_type, exc, tb):
        self.db.close()
