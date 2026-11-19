"""Render one thread's session read as dark and light SVG panels for the T3 theme.

The scorer writes a read (verdict, summary, five fixed measures, three ranked
next asks). This turns it into a CSS rule keyed by thread id that fills the
session desk slot in the BFD Agora theme. Text is HTML inside an SVG
foreignObject, so it wraps and clamps like the rest of the panel.
"""
from __future__ import annotations

import html
import json
import sys
from urllib.parse import quote

W, H = 248, 470
MEASURES = (("progress", "Progress"), ("momentum", "Momentum"), ("clarity", "Clarity"),
            ("risk", "Risk"), ("on_you", "On you"))
VERDICTS = {"ON TRACK": "live", "DONE": "live", "AT RISK": "risk", "STALLED": "risk", "NEEDS YOU": "gold"}
PALETTE = {
    "dark": {"ink": "#F4F4F5", "soft": "#C9C9CF", "muted": "#8A8A93", "dim": "#5C5C66", "line": "#2A2A30",
             "card": "#18181B", "live": "#5AE09A", "risk": "#FF7A59", "gold": "#FFC800", "goldtext": "#FFC800",
             "goldwash": "rgba(255,200,0,.07)", "goldline": "rgba(255,200,0,.55)", "hole": "#121214"},
    "light": {"ink": "#0B0B0C", "soft": "#3F3F46", "muted": "#71717A", "dim": "#A1A1AA", "line": "#E4E4E7",
              "card": "#FAFAFA", "live": "#14935A", "risk": "#D9480F", "gold": "#E8B400", "goldtext": "#8A6A00",
              "goldwash": "rgba(232,180,0,.10)", "goldline": "rgba(232,180,0,.65)", "hole": "#FFFFFF"},
}
HEAD = "Montserrat,-apple-system,system-ui,sans-serif"
BODY = "-apple-system,system-ui,Inter,sans-serif"
MONO = "ui-monospace,Menlo,monospace"
SAFE = " =:;,/'()-.!{}*"


def overall(s: dict) -> float:
    """One number for the ring: how well the thread is going, not who owes what."""
    return round((s["progress"] + s["momentum"] + s["clarity"] + (10 - s["risk"])) / 4, 1)


def _style(c: dict) -> str:
    clamp = "display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden"
    return (
        f"*{{box-sizing:border-box;margin:0}}"
        f".r{{width:{W}px;height:{H}px;overflow:hidden;color:{c['ink']};font-family:{BODY}}}"
        f".k{{display:flex;justify-content:space-between;font:700 9.5px/14px {HEAD};letter-spacing:.12em;text-transform:uppercase;color:{c['muted']}}}"
        f".k i{{font-style:normal;letter-spacing:.03em;text-transform:none;font-weight:600;color:{c['dim']}}}"
        f".v{{display:flex;gap:11px;align-items:center;margin:10px 0 12px;height:58px}}"
        f".g{{width:46px;height:46px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center}}"
        f".h{{width:37px;height:37px;border-radius:50%;background:{c['hole']};display:flex;align-items:center;justify-content:center;font:800 14px/1 {HEAD}}}"
        f".w{{font:800 11px/15px {HEAD};letter-spacing:.06em}}"
        f".s{{font:400 12px/16px {BODY};color:{c['soft']};{clamp};-webkit-line-clamp:3}}"
        f".m{{display:grid;grid-template-columns:70px 1fr 18px;gap:8px;align-items:center;height:19px;font:500 11.5px/1 {BODY};color:{c['soft']}}}"
        f".b{{display:grid;grid-template-columns:repeat(10,1fr);gap:2px}}"
        f".b u{{display:block;height:5px;border-radius:1px;background:{c['line']}}}"
        f".b u.f{{background:var(--f)}}"
        f".n{{text-align:right;font:700 11.5px/1 {MONO}}}"
        f".d{{height:1px;background:{c['line']};margin:14px 0 12px}}"
        f".a{{display:grid;grid-template-columns:14px 1fr 30px;gap:7px;padding:8px 9px;margin-top:6px;height:70px;border-radius:10px;border:1px solid {c['line']};background:{c['card']}}}"
        f".a.t{{border-color:{c['goldline']};background:linear-gradient({c['goldwash']},{c['goldwash']}),{c['card']}}}"
        f".a b{{font:800 11px/17px {HEAD};color:{c['dim']}}}"
        f".a .p{{text-align:right;font:700 11px/17px {MONO};color:{c['muted']}}}"
        f".a.t b,.a.t .p{{color:{c['goldtext']}}}"
        f".q{{font:600 12.5px/17px {BODY};{clamp};-webkit-line-clamp:2}}"
        f".y{{font:400 11px/15px {BODY};color:{c['muted']};margin-top:2px;{clamp};-webkit-line-clamp:1}}"
    )


def panel(read: dict, mode: str) -> str:
    c = PALETTE[mode]
    e = lambda t: html.escape(str(t), quote=True)
    s = read["scores"]
    o = overall(s)
    vcol = c[VERDICTS.get(read["verdict"], "live")]
    rows = []
    for key, label in MEASURES:
        v = max(0, min(10, int(s[key])))
        fill = c["risk"] if key == "risk" else c["gold"] if key == "on_you" else c["ink"]
        segs = "<u class='f'></u>" * v + "<u></u>" * (10 - v)
        rows.append(f"<div class='m'><span>{e(label)}</span><span class='b' style='--f:{fill}'>{segs}</span><span class='n'>{v}</span></div>")
    asks = "".join(
        f"<div class='a{' t' if n == 1 else ''}'><b>{n}</b><div><div class='q'>{e(a['ask'])}</div>"
        f"<div class='y'>{e(a.get('why', ''))}</div></div><span class='p'>{int(a['p'])}%</span></div>"
        for n, a in enumerate(read["asks"][:3], 1))
    doc = (
        f"<div xmlns='http://www.w3.org/1999/xhtml' class='r'><style>{_style(c)}</style>"
        f"<div class='k'><span>Session read</span><i>{e(read.get('scored', ''))}</i></div>"
        f"<div class='v'><div class='g' style='background:conic-gradient({vcol} 0 {o * 10:.0f}%,{c['line']} {o * 10:.0f}% 100%)'>"
        f"<div class='h'>{o:.1f}</div></div><div><div class='w' style='color:{vcol}'>{e(read['verdict'])}</div>"
        f"<div class='s'>{e(read['summary'])}</div></div></div>"
        + "".join(rows) +
        "<div class='d'></div><div class='k'><span>Next best asks</span><i>most likely first</i></div>"
        + asks + "</div>")
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>"
           f"<foreignObject x='0' y='0' width='{W}' height='{H}'>{doc}</foreignObject></svg>")
    return 'url("data:image/svg+xml,' + quote(svg, safe=SAFE) + '")'


def alt(read: dict) -> str:
    asks = "; ".join(f"{a['ask']} ({a['p']}%)" for a in read["asks"][:3])
    return json.dumps(f"Session read: {read['verdict'].lower()}. {read['summary']} Next best asks: {asks}.")


def rule(thread_id: str, read: dict, scope: str | None = None) -> str:
    sel = scope or f'aside[data-thread-details-panel][data-workspace-focus-key$=":{thread_id}"]'
    common = f'--bfd-desk-ar:{W}/{H};--bfd-desk-text:"";--bfd-desk-alt:{alt(read)}'
    return (f".dark {sel}{{{common};--bfd-desk-img:{panel(read, 'dark')}}}\n"
            f":root:not(.dark) {sel}{{{common};--bfd-desk-img:{panel(read, 'light')}}}\n")


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    scope = sys.argv[2] if len(sys.argv) > 2 else None
    sys.stdout.write("".join(rule(tid, r, scope) for tid, r in data.items()))
