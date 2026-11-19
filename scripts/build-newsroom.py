"""Synchronize the editable broadcast layout into the released T3 theme."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
theme = root / "themes/bfd-agora.json"
document = json.loads(theme.read_text())
marker = "/* BFD newsroom */"
base = document["css"].split(marker, 1)[0].rstrip()
document["css"] = base + "\n" + marker + "\n" + (root / "design/newsroom.css").read_text()
theme.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
