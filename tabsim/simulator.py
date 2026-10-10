"""Simulation engine: shared logic for every replacement policy."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Step:
    index: int                   # 1-based position in the request sequence
    tab: str                     # tab requested at this step
    frames: List[Optional[str]]  # frame contents AFTER the step
    is_hit: bool
    evicted: Optional[str] = None  # tab thrown out (None on a hit or free frame)


@dataclass
class Result:
    policy_name: str
    steps: List[Step] = field(default_factory=list)
    hits: int = 0
    faults: int = 0

    def hit_ratio(self):
        total = self.hits + self.faults
        return self.hits / total if total else 0.0

    def fault_ratio(self):
        total = self.hits + self.faults
        return self.faults / total if total else 0.0


class Simulator:
    def __init__(self, sequence, frame_count, policy):
        self.sequence = list(sequence)
        self.frame_count = frame_count
        self.policy = policy

    def run(self):
        frames = [None] * self.frame_count
        self.policy.reset(self.frame_count)
        result = Result(policy_name=self.policy.name)

        for time, tab in enumerate(self.sequence):
            slot = self._find_tab(frames, tab)
            is_hit = slot is not None
            evicted = None

            if is_hit:                                 # HIT: tab already loaded
                result.hits += 1
                self.policy.on_hit(tab, time, slot)
            else:                                      # FAULT: tab must be loaded
                result.faults += 1
                if None in frames:                     # free frame available
                    slot = frames.index(None)
                else:                                  # all full -> policy picks victim
                    slot = self.policy.choose_victim(frames, time, self.sequence)
                    evicted = frames[slot]
                frames[slot] = tab
                self.policy.on_load(tab, time, slot)

            result.steps.append(Step(time + 1, tab, list(frames), is_hit, evicted))
        return result

    @staticmethod
    def _find_tab(frames, tab):
        return frames.index(tab) if tab in frames else None
