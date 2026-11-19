# BFD T3 releases

This repository publishes the [team T3 theme](themes/bfd-agora.json). A merge to
`main` releases it. The enrolled computers fetch each release automatically and
compose the ticker from the sessions available on that computer.

The team runs [official upstream T3 Code Nightly](https://github.com/pingdotgg/t3code).

## Who runs this theme

| Where | How the theme arrives |
| --- | --- |
| Keith’s Pro, Air and Keith Cloud | Minion’s scheduled upkeep downloads the release, composes local stories and selects it with `t3 theme set`. Each Mac’s Nightly window uses its own T3 server. |
| Teammate cloud computers and client Minion images | The [keeper](https://github.com/black-flag-collective/minion-keith/blob/main/config/team-computers/t3_keeper.py) checks the configured theme URL on its regular interval. The web app served by that computer uses its theme. |
| Central hosted web app at `app.t3.codes` | Its browser profile stores its own appearance. To show a server’s current rundown, import that server’s installed `bfd-agora.json` in **Settings → Appearance** and choose **Update existing** when prompted. |
| Native T3 phone app | The native list shows the saved thread title. `NEEDS <NAME>:` identifies a human action, `UPDATE:` a finished result and `AUTOMATION:` a scheduled job. |

Run `t3 theme show` on the server to check that it selected `bfd-agora`. The installed
file is `userdata/themes/bfd-agora.json` under `T3CODE_HOME`, which defaults to
`~/.t3`. The ticker can give two machines different file hashes on the same release.

On the Pro, Air and Keith Cloud, `~/.local/state/minion-computer/t3-theme/applied.json`
records two SHA-256 hashes. Compare `releaseSha256` with the downloaded file on
`main` and `sha256` with the installed file. The teammate keeper records its installed
content hash in `runtime/keeper/theme` under `T3CODE_HOME`.

## Reading the forecasts

When a session has forecasts, its thread details show three next likely actions
ordered by their estimated likelihood. The percentages assume the next request is one of
the three suggestions. Opening the panel on a phone gives the full session title
its own line above the suggestions. A linked session can also show which computer
it came from.

## Why it is called "releases"

The repository was created to publish **BFD Agora**, a re-signed copy of each upstream nightly
with Black Flag's name and icon, as GitHub Releases. The team moved to official T3 Code
Nightly instead, so those builds have no users and the scheduled stamping is off. The
[`stamp-nightly`](.github/workflows/stamp-nightly.yml) workflow and its scripts remain for a
manual run, and the old builds remain under
[Releases](https://github.com/black-flag-collective/bfd-t3-releases/releases). Don't install
them. The theme kept the repository's name because every computer already fetches it from this URL.

## The sidebar

The sidebar is an update board. A thread's title and the app's own status decide where it sits,
never who is looking:

- **Needs Keith** or **Needs action**: `NEEDS <NAME>: <exact action>` titles, and any thread
  stopped on an approval, question or request. The heading says **Needs Keith** when every row
  names Keith, and **Needs action** for anyone else or a mix. Replies and send approvals
  (`NEEDS <NAME>: Reply to <person> — <subject>`, `NEEDS <NAME>: Approve send — <audience>: <subject>`)
  lead the group.
- **Updates**: `UPDATE: <result>`, finished work a person should know about. The native checkmark
  appears on hover or keyboard focus and settles the thread.
- **Working**: a turn is running now.
- **Automations**: `AUTOMATION: <plain name>` scheduled jobs, in compact one-line rows.
  Failed or limited runs turn red and stay in this group.
- **Open threads**: every other open thread. Agents have it; a failed or out-of-usage row says so.
- **Later**: the app's snoozed shelf.

Scheduled jobs settle their own thread at the end of each run. Automations are a normal
section below Working, not a sticky footer; they stay out of the ticker. Unsent drafts
stay out of every group and count.

A title that ends with a middle dot and a first name, as in `UPDATE: Invite sent · Eli`, shows
that person as the one who asked.
Portraits are embedded in the theme, so a new teammate needs a portrait added to it.
