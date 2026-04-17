import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

def retry_func(
    max_attempts: int = 3,
    min_wait: float = 10.0,
    max_wait: float = 60.0,
):
    return retry(
        stop=stop_after_attempt(max_attempt_number=max_attempts),
        wait=wait_exponential(multiplier=2, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(Exception),
        reraise=True,
        sleep=asyncio.sleep,
    )