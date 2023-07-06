import re
from itertools import count
from pathlib import Path
from typing import Optional

import lxml.builder
import lxml.etree

from azlyrics_api.models import Song


def export_to_xml(song: Song, path: Optional[str | Path] = None) -> str:
    """Export song to XML."""
    counter = count(2)
    tagged_lyrics = "[V1]\n" + re.sub(
        r"\n\n", lambda x: f"\n\n[V{next(counter)}]\n", song.lyrics
    )
    parsed_lyrics = ""
    for line in tagged_lyrics.splitlines():
        if line and not line.startswith("["):
            parsed_lyrics += f" {line}"
        else:
            parsed_lyrics += line
        parsed_lyrics += "\n"
    E = lxml.builder.ElementMaker()
    tree = E.song(E.title(song.title), E.author(song.artist), E.lyrics(parsed_lyrics))
    xml = lxml.etree.tostring(
        tree, encoding="UTF-8", xml_declaration=True, pretty_print=True
    ).decode()
    if path:
        path = Path(path)
        if path.is_dir():
            path /= f"{song.title} - {song.artist}"
        with open(path, "w") as fd:
            fd.write(xml)
    return xml
