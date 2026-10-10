"""Page (tab) replacement policies.

Every policy answers ONE question: when all frames are full and a new tab
must be loaded, which frame (slot) should be evicted?

Hooks called by the Simulator:
    reset(frame_count)            - start of a run
    on_hit(tab, time, slot)       - requested tab was already loaded
    on_load(tab, time, slot)      - tab was just placed into `slot`
    choose_victim(frames, time, sequence) -> slot index to evict
"""

from abc import ABC, abstractmethod
from collections import deque


class ReplacementPolicy(ABC):
    name = "Base"

    def reset(self, frame_count):
        self.frame_count = frame_count

    def on_hit(self, tab, time, slot):
        pass

    def on_load(self, tab, time, slot):
        pass

    @abstractmethod
    def choose_victim(self, frames, time, sequence):
        """Return the slot index (0..frame_count-1) to evict."""


class FIFOPolicy(ReplacementPolicy):
    """Evict the tab that has been loaded the longest, ignoring usage."""

    name = "FIFO"

    def reset(self, frame_count):
        super().reset(frame_count)
        self.queue = deque()  # slots in order of loading (oldest first)

    def on_load(self, tab, time, slot):
        if slot in self.queue:
            self.queue.remove(slot)
        self.queue.append(slot)

    def choose_victim(self, frames, time, sequence):
        return self.queue[0]


class LRUPolicy(ReplacementPolicy):
    """Evict the tab whose last use is the oldest."""

    name = "LRU"

    def reset(self, frame_count):
        super().reset(frame_count)
        self.last_used = {}  # tab -> time of most recent use

    def on_hit(self, tab, time, slot):
        self.last_used[tab] = time

    def on_load(self, tab, time, slot):
        self.last_used[tab] = time

    def choose_victim(self, frames, time, sequence):
        return min(range(len(frames)), key=lambda s: self.last_used[frames[s]])


class OptimalPolicy(ReplacementPolicy):
    """Evict the tab whose next use is farthest in the future (or never).

    Needs the whole sequence in advance, so it is only a benchmark.
    """

    name = "Optimal"

    def choose_victim(self, frames, time, sequence):
        future = sequence[time + 1:]
        best_slot, best_distance = 0, -1
        for slot, tab in enumerate(frames):
            try:
                distance = future.index(tab)
            except ValueError:  # never used again -> perfect victim
                return slot
            if distance > best_distance:
                best_slot, best_distance = slot, distance
        return best_slot


class ClockPolicy(ReplacementPolicy):
    """Second-chance / Clock: circular frames, a reference bit, a moving hand."""

    name = "Clock"

    def reset(self, frame_count):
        super().reset(frame_count)
        self.ref_bits = [0] * frame_count
        self.hand = 0

    def on_hit(self, tab, time, slot):
        self.ref_bits[slot] = 1

    def on_load(self, tab, time, slot):
        self.ref_bits[slot] = 1
        self.hand = (slot + 1) % self.frame_count  # hand moves past the new tab

    def choose_victim(self, frames, time, sequence):
        while True:
            if self.ref_bits[self.hand] == 0:
                return self.hand
            self.ref_bits[self.hand] = 0  # second chance used up
            self.hand = (self.hand + 1) % self.frame_count


ALL_POLICIES = [FIFOPolicy, LRUPolicy, OptimalPolicy, ClockPolicy]
