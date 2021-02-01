import logging
import os
import re
import ssl

from fastapi import FastAPI
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise

log = logging.getLogger("uvicorn")

config = re.match("postgres://(.*?):(.*?)@(.*?)/(.*)", os.environ.get("DATABASE_URL", ''))
try:
    DB_USER, DB_PASS, DB_HOST, DB = config.groups()
except AttributeError:
    DB_USER, DB_PASS, DB_HOST, DB = '', '', '', ''

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": DB,
                "host": DB_HOST.split(":")[0],
                "password": DB_PASS,
                "port": int(DB_HOST.split(":")[1]),
                "user": DB_USER,
                "ssl": context,  # Here we pass in the SSL context
            },
        },
    },
    "apps": {
        "models": {
            "models": ["app.models.tortoise", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        add_exception_handlers=True,
        generate_schemas=os.environ.get("GENERATE_SCHEMAS", default=False),
    )


async def generate_test_schema() -> None:
    log.info("Initializing Tortoise...")

    await Tortoise.init(
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["models.tortoise"]},
    )
    log.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(generate_test_schema())
