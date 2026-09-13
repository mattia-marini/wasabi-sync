"""Parsing and editing REAPER project (``.rpp``) files.

The ``.rpp`` format is line-oriented: a block opens with ``<NAME ...``
and closes with a line containing only ``>``. A track block
(``<TRACK ...``) carries, among others, these attributes:

* ``NAME "..."`` — the track name.
* ``MAINSEND <enabled> <...>`` — ``enabled`` is 1 when the track sends
  audio directly to the master/parent, 0 when it does not.
* ``MUTESOLO <mute> <solo> <defeat> ...`` — ``mute`` is 1 when the
  track is muted, 0 when unmuted.

Only track-level metadata is read; nested blocks (FX chains, items,
sources) are left untouched so a file can be edited and written back
without disturbing their contents.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class RppTrack:
    """Metadata for a single track in an ``.rpp`` document."""

    index: int
    name: str
    muted: bool
    sends_to_master: bool


@dataclass
class RppProject:
    """The tracks parsed out of an ``.rpp`` document."""

    tracks: list[RppTrack] = field(default_factory=list)

    @property
    def master_tracks(self) -> list[RppTrack]:
        """Tracks that send audio directly to the master/parent."""
        return [track for track in self.tracks if track.sends_to_master]


_TRACK_OPEN = re.compile(r"<TRACK(?:\s|\{|\>)")
_MUTESOLO_MUTE = re.compile(r"^(\s*MUTESOLO\s+)[01](?=\s|$)")


def parse_rpp(text: str) -> RppProject:
    """Parse the track metadata out of an ``.rpp`` document."""
    tracks = [
        _to_track(index, _track_fields(attributes))
        for index, attributes in _iter_track_attributes(text.splitlines())
    ]
    return RppProject(tracks=tracks)


def unmute_master_tracks(text: str) -> tuple[str, list[str]]:
    """Unmute muted master-sending tracks; return ``(new_text, names)``.

    Only tracks that send audio directly to the master are touched: their
    ``MUTESOLO`` mute flag is flipped from 1 to 0. Everything else in the
    document is preserved byte-for-byte.
    """
    lines = text.splitlines(keepends=True)
    unmuted: list[str] = []
    for index, attributes in _iter_track_attributes(lines):
        name, muted, sends_to_master, mutesolo_line = _track_fields(attributes)
        if sends_to_master and muted and mutesolo_line is not None:
            lines[mutesolo_line] = _set_mute(lines[mutesolo_line], muted=False)
            unmuted.append(name or f"Track {index}")
    return "".join(lines), unmuted


def _iter_track_attributes(
    lines: list[str],
) -> Iterator[tuple[int, list[tuple[int, list[str]]]]]:
    """Yield ``(track_index, [(line_no, tokens), ...])`` for each track.

    Only a track's own attribute lines are collected — scanning stops at
    the first nested block (``<...``) or the closing ``>``.
    """
    index = 0
    track_index = 0
    while index < len(lines):
        if _TRACK_OPEN.match(lines[index].lstrip()):
            track_index += 1
            attributes: list[tuple[int, list[str]]] = []
            cursor = index + 1
            while cursor < len(lines):
                stripped = lines[cursor].strip()
                if stripped.startswith("<") or stripped.startswith(">"):
                    break
                attributes.append((cursor, _tokenize(stripped)))
                cursor += 1
            yield track_index, attributes
            index = cursor
        else:
            index += 1


def _track_fields(
    attributes: list[tuple[int, list[str]]],
) -> tuple[str, bool, bool, int | None]:
    """Return ``(name, muted, sends_to_master, mutesolo_line_no)``."""
    name = ""
    muted = False
    sends_to_master = True
    mutesolo_line: int | None = None
    for line_no, tokens in attributes:
        if not tokens:
            continue
        key = tokens[0].upper()
        if key == "NAME" and len(tokens) > 1:
            name = tokens[1]
        elif key == "MAINSEND" and len(tokens) > 1:
            sends_to_master = tokens[1] != "0"
        elif key == "MUTESOLO":
            muted = len(tokens) > 1 and tokens[1] == "1"
            mutesolo_line = line_no
    return name, muted, sends_to_master, mutesolo_line


def _to_track(index: int, fields: tuple[str, bool, bool, int | None]) -> RppTrack:
    name, muted, sends_to_master, _ = fields
    return RppTrack(
        index=index,
        name=name or f"Track {index}",
        muted=muted,
        sends_to_master=sends_to_master,
    )


def _set_mute(line: str, muted: bool) -> str:
    return _MUTESOLO_MUTE.sub(r"\g<1>" + ("1" if muted else "0"), line, count=1)


def _tokenize(line: str) -> list[str]:
    """Split a line into tokens, honouring double-quoted strings."""
    tokens: list[str] = []
    index = 0
    length = len(line)
    while index < length:
        while index < length and line[index].isspace():
            index += 1
        if index >= length:
            break
        if line[index] == '"':
            index += 1
            start = index
            while index < length and line[index] != '"':
                index += 1
            tokens.append(line[start:index])
            index += 1
        else:
            start = index
            while index < length and not line[index].isspace():
                index += 1
            tokens.append(line[start:index])
    return tokens
