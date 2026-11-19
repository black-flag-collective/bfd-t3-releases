"""Synchronize the editable broadcast layout into the released T3 theme."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
theme = root / "themes/bfd-agora.json"
document = json.loads(theme.read_text())
marker = "/* BFD newsroom */"
base = document["css"].split(marker, 1)[0].rstrip()
source = (root / "design/newsroom.css").read_text()
# Leave standalone author notes in the source so server-local stories have room.
lines = [line for line in source.splitlines() if not re.fullmatch(r"\s*/\*[^*]*\*/\s*", line)]
packed = "\n".join(lines)
# These delimiters already separate CSS tokens. Preserve escaped line breaks in strings.
if "\\\n" not in packed:
    packed = "\n".join(line.lstrip(" \t") for line in lines)
    packed = re.sub(r"(?<!\\)([{};])\n", r"\1", packed)
document["css"] = "\n".join([base, marker, packed, ""])
theme.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
