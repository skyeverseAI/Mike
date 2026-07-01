import time
import asyncio

async def fetch_case(case_id):
    print(f"Fetching case {case_id}...")
    await asyncio.sleep(2)  # pretending this is a slow network call
    print(f"Got case {case_id}")
    return f"Case data for {case_id}"

async def main():
    start = time.perf_counter()
    
    # TODO: call fetch_case() for case_ids 1, 2, and 3
    case1, case2, case3 = await asyncio.gather(
        fetch_case(1),
        fetch_case(2),
        fetch_case(3))

    elapsed = time.perf_counter() - start
    print(f"Total time: {elapsed:.2f}s")

asyncio.run(main())