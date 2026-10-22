#!/usr/bin/env python3
"""Offline transposition of chord roots and slash bass notes."""
import argparse
import re

SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
ROOT = re.compile(r"(?<![A-Za-z])([A-G](?:#|b)?)(?=(?:maj|min|dim|aug|sus|add|m|M|[0-9]|/|\b))")


def transpose(text, steps, prefer_flats=False):
    names = {"C": 0, "B#": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
             "E": 4, "Fb": 4, "E#": 5, "F": 5, "F#": 6, "Gb": 6,
             "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10,
             "B": 11, "Cb": 11}
    scale = FLAT if prefer_flats else SHARP
    return ROOT.sub(lambda m: scale[(names[m.group(1)] + steps) % 12], text)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("semitones", type=int)
    p.add_argument("chords", nargs="+")
    p.add_argument("--flats", action="store_true")
    a = p.parse_args()
    print(transpose(" ".join(a.chords), a.semitones, a.flats))
