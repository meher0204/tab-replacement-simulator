"""Input handling: parsing, validation and preset browsing workloads."""

import random


def _random_sequence(length=30, tabs="ABCDEFGH", seed=42):
    rng = random.Random(seed)  # fixed seed -> repeatable results
    return [rng.choice(tabs) for _ in range(length)]


PRESETS = {
    # name: (description, sequence, suggested frames)
    "demo": (
        "Small demo from the project idea",
        list("ABCABDADBC"),
        3,
    ),
    "textbook": (
        "Classic textbook reference string (FIFO 15, LRU 12, Optimal 9 with 3 frames)",
        "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1".split(),
        3,
    ),
    "revisit": (
        "User keeps going back to a few favourite tabs (high locality)",
        list("AABABCABACABADABAEABAB"),
        3,
    ),
    "random": (
        "User opens tabs at random (no locality)",
        _random_sequence(),
        3,
    ),
    "cyclic": (
        "User cycles through 4 tabs with only 3 frames (LRU's worst case)",
        list("ABCD" * 6),
        3,
    ),
    "belady": (
        "Belady's anomaly string: FIFO faults go UP when frames go 3 -> 4",
        "1 2 3 4 1 2 5 1 2 3 4 5".split(),
        3,
    ),
}


def parse_input(text):
    """'A B C A' or 'A,B,C,A' or 'ABCA' -> ['A','B','C','A'] (case-insensitive)."""
    text = text.strip()
    if not text:
        return []
    if "," in text:
        tokens = text.split(",")
    elif " " in text:
        tokens = text.split()
    else:
        tokens = list(text)
    return [tok.strip().upper() for tok in tokens if tok.strip()]


def validate(sequence, frame_count):
    """Raise ValueError with a friendly message if the input is unusable."""
    if not sequence:
        raise ValueError("The tab sequence is empty.")
    if not isinstance(frame_count, int) or frame_count < 1:
        raise ValueError("Number of frames must be a whole number of at least 1.")
    if frame_count > 20:
        raise ValueError("Number of frames is limited to 20 to keep tables readable.")


def get_preset(name):
    """Return (description, sequence, frames) for a preset name."""
    key = name.lower()
    if key not in PRESETS:
        raise ValueError(f"Unknown preset '{name}'. Choose from: {', '.join(PRESETS)}")
    description, sequence, frames = PRESETS[key]
    return description, list(sequence), frames
