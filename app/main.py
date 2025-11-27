import uvicorn
from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar import Litestar, get

from app.alchemy_config import alchemy_config as config


@get("/")
async def hello_world() -> dict[str, str]:
    return {"message": "Hello, World!"}


app = Litestar(
    [hello_world],
    plugins=[SQLAlchemyPlugin(config=config)],
)

