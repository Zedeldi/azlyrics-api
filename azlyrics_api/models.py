from dataclasses import dataclass


@dataclass
class Song:
    """Dataclass to store information about a song."""

    title: str
    artist: str
    lyrics: str
    url: str
