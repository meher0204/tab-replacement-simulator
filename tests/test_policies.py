"""Unit tests. Run from the project root with:  python -m unittest -v"""

import unittest

from tabsim.policies import ClockPolicy, FIFOPolicy, LRUPolicy, OptimalPolicy
from tabsim.simulator import Simulator
from tabsim.workloads import PRESETS, parse_input, validate

TEXTBOOK = "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1".split()
BELADY = "1 2 3 4 1 2 5 1 2 3 4 5".split()


def faults(policy_cls, seq, frames):
    return Simulator(seq, frames, policy_cls()).run().faults


class TestKnownResults(unittest.TestCase):
    def test_textbook_fifo(self):
        self.assertEqual(faults(FIFOPolicy, TEXTBOOK, 3), 15)

    def test_textbook_lru(self):
        self.assertEqual(faults(LRUPolicy, TEXTBOOK, 3), 12)

    def test_textbook_optimal(self):
        self.assertEqual(faults(OptimalPolicy, TEXTBOOK, 3), 9)

    def test_belady_anomaly_fifo(self):
        self.assertEqual(faults(FIFOPolicy, BELADY, 3), 9)
        self.assertEqual(faults(FIFOPolicy, BELADY, 4), 10)  # more frames, MORE faults

    def test_lru_has_no_belady_anomaly(self):
        self.assertLessEqual(faults(LRUPolicy, BELADY, 4), faults(LRUPolicy, BELADY, 3))


class TestInvariants(unittest.TestCase):
    def test_optimal_never_worse(self):
        for name, (_, seq, frames) in PRESETS.items():
            best = faults(OptimalPolicy, seq, frames)
            for cls in (FIFOPolicy, LRUPolicy, ClockPolicy):
                self.assertLessEqual(best, faults(cls, seq, frames), f"{name}/{cls.name}")

    def test_hits_plus_faults_equals_requests(self):
        for cls in (FIFOPolicy, LRUPolicy, OptimalPolicy, ClockPolicy):
            r = Simulator(TEXTBOOK, 3, cls()).run()
            self.assertEqual(r.hits + r.faults, len(TEXTBOOK))

    def test_one_frame_everything_faults_unless_repeat(self):
        r = Simulator(list("AABB"), 1, FIFOPolicy()).run()
        self.assertEqual((r.hits, r.faults), (2, 2))

    def test_frames_never_exceed_capacity_and_hold_no_duplicates(self):
        for cls in (FIFOPolicy, LRUPolicy, OptimalPolicy, ClockPolicy):
            for step in Simulator(TEXTBOOK, 3, cls()).run().steps:
                loaded = [f for f in step.frames if f]
                self.assertLessEqual(len(loaded), 3)
                self.assertEqual(len(loaded), len(set(loaded)))

    def test_cyclic_pattern_lru_and_fifo_always_fault(self):
        seq = list("ABCD" * 6)
        self.assertEqual(faults(LRUPolicy, seq, 3), len(seq))
        self.assertEqual(faults(FIFOPolicy, seq, 3), len(seq))
        self.assertLess(faults(OptimalPolicy, seq, 3), len(seq))


class TestInput(unittest.TestCase):
    def test_parse_formats(self):
        self.assertEqual(parse_input("a b c"), ["A", "B", "C"])
        self.assertEqual(parse_input("a,b,c"), ["A", "B", "C"])
        self.assertEqual(parse_input("abc"), ["A", "B", "C"])
        self.assertEqual(parse_input("10 20 10"), ["10", "20", "10"])
        self.assertEqual(parse_input("   "), [])

    def test_validate_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            validate([], 3)
        with self.assertRaises(ValueError):
            validate(["A"], 0)
        with self.assertRaises(ValueError):
            validate(["A"], 99)
        validate(["A"], 3)  # fine


if __name__ == "__main__":
    unittest.main()
