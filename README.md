# token_bucket

A monotonic token bucket rate limiter for Python. Standard library only, no dependencies.

## Usage

```python
from token_bucket import TokenBucket
import time

bucket = TokenBucket(capacity=10, rate=2)  # burst of 10, 2 tokens/sec
ok = bucket.take(1)  # True if a token was available
ok = bucket.take(5)  # False if not enough tokens
available = bucket.tokens()  # current token count (refilled lazily)
```

A fake clock can be injected for testing:

```python
fake = [0.0]
def clock():
    return fake[0]
bucket = TokenBucket(capacity=10, rate=2, clock=clock)
fake[0] += 1.0  # advance time
```

## Why

This exists for the common case where you want to limit the rate of some action with
allowance for short bursts, without pulling in a heavier dependency. The design is
single-threaded and stateless between calls: refill is computed lazily from the last
seen time, so there is no background thread and no lock. That makes it cheap to
instantiate many small buckets. The trade-off is that it is not safe to share one
bucket across threads without external synchronization.

## Edge case

If the injected clock goes backward, refill is skipped rather than applied negatively.
The bucket's last-seen time is only updated when the clock moves forward. A request
larger than the bucket's capacity always returns `False`; it never partially consumes
tokens.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Contributing

Issues and pull requests are welcome. Please keep the dependency list empty —
that constraint is the point of the project, not an oversight.

