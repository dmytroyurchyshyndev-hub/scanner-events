from __future__ import annotations

import asyncio
import time
import logging
from functools import wraps
from typing import Dict, Callable

from web3 import AsyncWeb3
from web3.exceptions import (
    ProviderConnectionError,
    TimeExhausted,
    BlockNotFound,
    TransactionNotFound,
)
from web3.middleware import ExtraDataToPOAMiddleware

logger = logging.getLogger("async_web3_adapter")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s"
))
logger.addHandler(handler)


def retry_web3(max_seconds: int = 30):

    def decorator(func):
        @wraps(func)
        async def wrapper(self: "AsyncWeb3Adapter", *args, **kwargs):
            start = time.time()
            attempt = 1

            while True:
                try:
                    return await func(self, *args, **kwargs)

                except (
                    ProviderConnectionError,
                    TimeExhausted,
                    BlockNotFound,
                    TransactionNotFound,
                ) as exc:

                    elapsed = time.time() - start
                    remaining = max_seconds - elapsed

                    logger.warning(
                        f"[RPC: {self.rpc_url}] Web3 error on attempt #{attempt}: {type(exc).__name__} — {exc}. "
                        f"Retrying... time left: {remaining:.1f}s"
                    )

                    if remaining <= 0:
                        logger.error(
                            f"[RPC: {self.rpc_url}] Retry timeout exceeded ({max_seconds}s). Raising error."
                        )
                        raise exc

                    await asyncio.sleep(1)
                    attempt += 1

                except Exception as exc:
                    logger.error(
                        f"[RPC: {self.rpc_url}] Non-Web3 error: {type(exc).__name__} — {exc}"
                    )
                    raise

        return wrapper
    return decorator


class AsyncWeb3Adapter:
    _instances: Dict[str, "AsyncWeb3Adapter"] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(
        cls,
        rpc_url: str,
        request_timeout: int = 10,
    ) -> "AsyncWeb3Adapter":
        async with cls._lock:
            if rpc_url in cls._instances:
                logger.info(f"[RPC: {rpc_url}] Using cached Web3 adapter instance")
                return cls._instances[rpc_url]

            logger.info(f"[RPC: {rpc_url}] Creating new Web3 adapter instance")

            instance = cls(
                rpc_url=rpc_url,
                request_timeout=request_timeout,
                _internal=True,
            )
            cls._instances[rpc_url] = instance
            return instance

    def __init__(
        self,
        rpc_url: str,
        request_timeout: int = 10,
        _internal: bool = False,
    ):
        if not _internal:
            raise RuntimeError("Use AsyncWeb3Adapter.get_instance()")

        self.rpc_url = rpc_url
        self.request_timeout = request_timeout
        self.w3 = self._create_client()

    def _create_client(self) -> AsyncWeb3:
        logger.info(f"[RPC: {self.rpc_url}] Initializing AsyncWeb3 client")

        w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(
                self.rpc_url,
                request_kwargs={"timeout": self.request_timeout},
            )
        )
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        return w3

    @retry_web3(max_seconds=30)
    async def ensure_connection(self) -> bool:
        ok = await self.w3.is_connected()
        if not ok:
            raise ProviderConnectionError("is_connected() returned False")
        logger.info(f"[RPC: {self.rpc_url}] Connection OK")
        return True

    @retry_web3(max_seconds=30)
    async def get_latest_block(self) -> int:
        block = await self.w3.eth.block_number
        logger.info(f"[RPC: {self.rpc_url}] Latest block = {block}")
        return block
