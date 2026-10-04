from rich import print
import time
import asyncio

async def endpoint(route):
    print(f">> handling {route}")
    await asyncio.sleep(1)
    print(f"<< response {route}")
    return route

async def server():
    tests = [
        "GET /shipment?id=1",
        "PATCH /shipment?id=5",
        "GET /shipment?id=3"
    ]

    start = time.perf_counter()

    async with asyncio.TaskGroup() as task_group:
        tasks = [task_group.create_task(endpoint(route)) for route in tests]

    for task in tasks:
        print(task.result())

    end = time.perf_counter()

    print(f"Total time: {end-start:.2f}s")

asyncio.run(server())
