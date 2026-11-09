"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """Relative sentence-length variability. Higher means more varied.

    For AI-ish writing, sentence lengths are often unusually regular, so this
    measure drops on machine-like prose. We put it on a comparable scale by
    dividing by the mean sentence length.
    """
    parts = sentences(text)
    if len(parts) < 2:
        return 0.0

    lengths = [len(words(p)) for p in parts]
    mean_len = sum(lengths) / len(lengths)
    if mean_len == 0:
        return 0.0

    spread = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
    return spread / mean_len


def type_token_ratio(text: str) -> float:
    """Unique words divided by total words; higher means more varied vocabulary."""
    words_list = words(text)
    if not words_list:
        return 0.0
    unique = set(words_list)
    return len(unique) / len(words_list)


def punctuation_density(text: str) -> float:
    """Punctuation count relative to the length of the text."""
    if not text:
        return 0.0

    punctuation = re.findall(r"[;:,.!?—\-\(\)\[\]]", text)
    length = len(text)
    if length == 0:
        return 0.0
    return len(punctuation) / length


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """0–1 AI-likelihood based on stylistic shape of the text."""
    if not isinstance(text, str):
        raise ValueError("text must be a string")

    text = text.strip()
    if not text:
        return 0.5

    spread = sentence_length_spread(text)
    vocab = type_token_ratio(text)
    punct = punctuation_density(text)

    spread_component = 1.0 / (1.0 + spread)
    vocab_component = 1.0 - vocab
    punctuation_component = 1.0 - min(punct / 0.06, 1.0)

    score = (
        0.45 * spread_component
        + 0.35 * vocab_component
        + 0.20 * punctuation_component
    )
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nAll zeros? These are stubs — Milestone 4 is where you build them.")
