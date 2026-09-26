from __future__ import annotations

import time
from typing import Callable


class TokenBucket:
    """
    A monotonic token bucket rate limiter.

    The bucket has a ``capacity`` (burst limit) and refills at a steady
    ``rate`` tokens per second. ``take(n)`` deducts ``n`` tokens if available
    and returns ``True``; otherwise it returns ``False`` and leaves the bucket
    untouched.

    All time comes from an injectable ``clock`` callable returning seconds
    (default ``time.monotonic``). Refill is computed lazily on each call:
    we store ``self._tokens`` and ``self._last``, and on every operation we
    add ``elapsed * rate`` (capped at ``capacity``) before attempting the
    deduction. This avoids background threads and keeps the limiter
    stateless between calls, which is easy to reason about.

    Refill only happens monotonically forward: if the clock returns a value
    less than or equal to the last seen time, we skip the refill step rather
    than clamp the clock. This keeps behavior predictable under fake clocks
    and guards against clock drift.
    """

    def __init__(
        self,
        *,
        capacity: float,
        rate: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if rate <= 0:
            raise ValueError("rate must be positive")
        self._capacity = float(capacity)
        self._rate = float(rate)
        self._clock = clock
        self._tokens = float(capacity)
        self._last = float(clock())

    @property
    def capacity(self) -> float:
        return self._capacity

    @property
    def rate(self) -> float:
        return self._rate

    def _refill(self, now: float) -> None:
        if now <= self._last:
            return
        elapsed = now - self._last
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        self._last = now

    def tokens(self) -> float:
        now = float(self._clock())
        self._refill(now)
        return self._tokens

    def take(self, n: float = 1.0) -> bool:
        if n <= 0:
            raise ValueError("n must be positive")
        if n > self._capacity:
            return False
        now = float(self._clock())
        self._refill(now)
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False
