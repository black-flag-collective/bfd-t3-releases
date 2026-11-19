# BFD T3 releases

This repository publishes the **team T3 theme**. Every Black Flag T3 Code install runs
[`themes/bfd-agora.json`](themes/bfd-agora.json) from `main`. A merge to `main` is a theme
release: the cloud computers pick it up on their own and desktops pick it up with one command.

The T3 app itself is **official T3 Code Nightly** from upstream
([`pingdotgg/t3code`](https://github.com/pingdotgg/t3code)), unmodified. Nobody at Black Flag
runs a fork or a rebuilt app.

## Who runs this theme

| Where | T3 app | How the theme arrives |
| --- | --- | --- |
| Personal cloud computers (`bfd-t3-<person>` on Fly) and client Minions | Upstream T3 Code Nightly, kept current by the [keeper](https://github.com/black-flag-collective/minion-keith/blob/main/config/team-computers/t3_keeper.py) | The keeper downloads this file from `main` and runs `t3 theme set` whenever it changes. The web app those computers serve shows it. |
| A desktop Mac | `T3 Code (Nightly).app` from upstream | The desktop shows the theme of the T3 server on the same Mac, not of a computer it is linked to. Run the commands below once per change, or import the file in **Settings → Appearance**. |
| The T3 phone app | Upstream | Phones show no theme. The `NEEDS <NAME>:` and `READ:` title prefixes are the whole signal there. |

```sh
curl -fsSL -o /tmp/bfd-agora.json https://raw.githubusercontent.com/black-flag-collective/bfd-t3-releases/main/themes/bfd-agora.json
t3 theme set /tmp/bfd-agora.json
```

To check a computer, run `t3 theme show`. It should name `bfd-agora`, and the installed file's
`css` should match the one on `main`.

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
