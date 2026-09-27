import math
import unittest

from token_bucket import TokenBucket


def make_clock():
    t = [0.0]

    def now():
        return t[0]

    return now, t


class TestTokenBucket(unittest.TestCase):
    def test_initial_take_up_to_capacity(self):
        clock, _ = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        for _ in range(5):
            self.assertTrue(b.take(1))
        self.assertFalse(b.take(1))

    def test_refill_after_time(self):
        clock, t = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        for _ in range(5):
            self.assertTrue(b.take(1))
        self.assertFalse(b.take(1))
        t[0] += 3.0
        self.assertTrue(b.take(1))
        self.assertTrue(b.take(1))
        self.assertTrue(b.take(1))
        self.assertFalse(b.take(1))

    def test_refill_caps_at_capacity(self):
        clock, t = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        b.take(5)
        self.assertEqual(b.tokens(), 0.0)
        t[0] += 100.0
        self.assertEqual(b.tokens(), 5.0)

    def test_burst_capacity(self):
        clock, _ = make_clock()
        b = TokenBucket(capacity=10, rate=1, clock=clock)
        self.assertTrue(b.take(10))
        self.assertFalse(b.take(1))

    def test_take_more_than_capacity_returns_false(self):
        clock, _ = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        self.assertFalse(b.take(6))

    def test_take_fractional(self):
        clock, t = make_clock()
        b = TokenBucket(capacity=1, rate=1, clock=clock)
        self.assertTrue(b.take(0.5))
        self.assertTrue(b.take(0.5))
        self.assertFalse(b.take(0.5))
        t[0] += 0.5
        self.assertTrue(b.take(0.5))

    def test_insufficient_tokens_leaves_bucket_untouched(self):
        clock, t = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        b.take(4)
        before = b.tokens()
        self.assertFalse(b.take(2))
        self.assertEqual(b.tokens(), before)

    def test_clock_non_monotonic_no_refill(self):
        clock, t = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        b.take(5)
        t[0] = -1.0
        self.assertEqual(b.tokens(), 0.0)
        t[0] = 0.0
        self.assertEqual(b.tokens(), 0.0)

    def test_invalid_capacity(self):
        clock, _ = make_clock()
        with self.assertRaises(ValueError):
            TokenBucket(capacity=0, rate=1, clock=clock)
        with self.assertRaises(ValueError):
            TokenBucket(capacity=-1, rate=1, clock=clock)

    def test_invalid_rate(self):
        clock, _ = make_clock()
        with self.assertRaises(ValueError):
            TokenBucket(capacity=5, rate=0, clock=clock)
        with self.assertRaises(ValueError):
            TokenBucket(capacity=5, rate=-1, clock=clock)

    def test_invalid_n(self):
        clock, _ = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        with self.assertRaises(ValueError):
            b.take(0)
        with self.assertRaises(ValueError):
            b.take(-1)

    def test_properties(self):
        clock, _ = make_clock()
        b = TokenBucket(capacity=7, rate=2, clock=clock)
        self.assertEqual(b.capacity, 7.0)
        self.assertEqual(b.rate, 2.0)

    def test_partial_refill_between_takes(self):
        clock, t = make_clock()
        b = TokenBucket(capacity=4, rate=2, clock=clock)
        self.assertTrue(b.take(4))
        t[0] += 1.0
        self.assertTrue(b.take(2))
        self.assertFalse(b.take(1))

    def test_tokens_reports_available_without_consuming(self):
        clock, _ = make_clock()
        b = TokenBucket(capacity=5, rate=1, clock=clock)
        self.assertEqual(b.tokens(), 5.0)
        self.assertEqual(b.tokens(), 5.0)


if __name__ == "__main__":
    unittest.main()
