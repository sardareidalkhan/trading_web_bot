import sys
import asyncio
import uvicorn
import logging
import os

def configure_asyncio():
    if sys.platform.startswith("win"):
        policy = asyncio.WindowsProactorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def start_server():
    port = int(os.environ.get("PORT", 8000))  # ✅ Read port from env for Render
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # ✅ Required for Render/Docker
        port=port,
        reload=False,
        workers=1,
    )

if __name__ == "__main__":
    configure_asyncio()
    configure_logging()
    start_server()
