"""Tests for .rpp parsing and editing."""

from __future__ import annotations

from wasabi_sync.reaper.rpp import parse_rpp, unmute_master_tracks

SAMPLE = """<REAPER_PROJECT 0.1 "7.0" 1710000000
  <TRACK {G1}
    NAME "Drums"
    MUTESOLO 0 0 0
    MAINSEND 1 0
  >
  <TRACK {G2}
    NAME "Bass"
    MUTESOLO 1 0 0
    MAINSEND 1 0
  >
  <TRACK {G3}
    NAME "Keys"
    MUTESOLO 1 0 0
    MAINSEND 0 0
  >
  <TRACK {G4}
    NAME ""
    MAINSEND 1 0
  >
>
"""


def test_parse_rpp_extracts_tracks():
    project = parse_rpp(SAMPLE)
    assert len(project.tracks) == 4
    drums, bass, keys, unnamed = project.tracks
    assert (drums.name, drums.muted, drums.sends_to_master) == ("Drums", False, True)
    assert (bass.name, bass.muted, bass.sends_to_master) == ("Bass", True, True)
    assert (keys.name, keys.muted, keys.sends_to_master) == ("Keys", True, False)
    assert (unnamed.name, unnamed.muted, unnamed.sends_to_master) == ("Track 4", False, True)


def test_master_tracks_excludes_others():
    assert [track.name for track in parse_rpp(SAMPLE).master_tracks] == [
        "Drums",
        "Bass",
        "Track 4",
    ]


def test_unmute_master_tracks():
    new_text, unmuted = unmute_master_tracks(SAMPLE)
    assert unmuted == ["Bass"]
    by_name = {track.name: track for track in parse_rpp(new_text).tracks}
    assert by_name["Bass"].muted is False
    assert by_name["Drums"].muted is False
    assert by_name["Keys"].muted is True  # non-master, left untouched


def test_unmute_preserves_unrelated_content():
    new_text, _ = unmute_master_tracks(SAMPLE)
    assert new_text.count("MUTESOLO 0 0 0") == 2  # Drums (already) + Bass (now)
    assert new_text.count("MUTESOLO 1 0 0") == 1  # Keys still muted
    assert "MAINSEND 0 0" in new_text
    assert '<REAPER_PROJECT 0.1 "7.0" 1710000000' in new_text


def test_unmute_no_changes_when_nothing_muted():
    text = (
        '<REAPER_PROJECT 0.1 "7.0" 1\n  <TRACK {G1}\n    NAME "A"\n'
        "    MUTESOLO 0 0 0\n    MAINSEND 1 0\n  >\n>\n"
    )
    new_text, unmuted = unmute_master_tracks(text)
    assert unmuted == []
    assert new_text == text


def test_unmute_handles_crlf_and_no_trailing_newline():
    text = (
        '<REAPER_PROJECT 0.1 "7.0" 1\r\n  <TRACK {G1}\r\n    NAME "A"\r\n'
        "    MUTESOLO 1 0 0\r\n    MAINSEND 1 0\r\n  >\r\n>"
    )
    new_text, unmuted = unmute_master_tracks(text)
    assert unmuted == ["A"]
    assert "MUTESOLO 0 0 0" in new_text
    assert "\r\n" in new_text
