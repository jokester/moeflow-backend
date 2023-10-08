import asyncio, threading
from typing import Coroutine


def init_event_loop() -> asyncio.AbstractEventLoop:
    def start_loop(l: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(l)
        l.run_forever()

    loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_loop, args=(loop,), daemon=True)
    t.start()
    return loop


event_loop = init_event_loop()


def wait_task(task: asyncio.Future | Coroutine):
    """等待并发任务"""
    return asyncio.run_coroutine_threadsafe(task, event_loop)
