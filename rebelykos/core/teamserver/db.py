import aiosqlite
import sqlite3
import logging
import asyncio
import uuid

from rebelykos.core.utils import get_path_in_data_folder


class RLDatabase:

    def __init__(self, db_path=get_path_in_data_folder("rl.db")):
        self.db_path = db_path

    @staticmethod
    def create_db_and_schema(db_path=get_path_in_data_folder("rl.db")):
        with sqlite3.connect(db_path) as db:
            db.execute('''CREATE TABLE "profiles" (
                            "id" integer PRIMARY KEY,
                            "profile" text,
                            "access_key_id" text,
                            "secret_access_key" text,
                            "region" text,
                            "session_token" text,
                            UNIQUE(profile)
                        )''')

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

    def remove(self, profile):
        with self.db:
            try:
                self.db.execute("DELETE FROM profiles WHERE profile = ?",
                                [profile])
                msg = f"Remove '{profile}' from the database"
                logging.debug(msg)
            except sqlite3.IntegrityError:
                msg = f"Could not remove {profile} ffrom the database"
                logging.debug(msg)
            return msg

    def __enter__(self):
        self.db = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, exec_type, exc, tb):
        self.db.commit()
        self.db.close()
