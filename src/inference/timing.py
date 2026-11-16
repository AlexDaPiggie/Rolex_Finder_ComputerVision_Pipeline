"""Tiny timing helper. Prints one log line per phase and can collect the values in a dict."""
import time
from contextlib import contextmanager

# Filled by warm_models() at container start, exposed on /health
STARTUP: dict[str, float] = {}


@contextmanager
def timed(label: str, sink: dict | None = None):
    start = time.perf_counter()
    try:
        yield
    finally:
        ms = round((time.perf_counter() - start) * 1000, 1)
        if sink is not None:
            sink[label] = ms
        print(f"[timing] {label}={ms}ms", flush=True)
