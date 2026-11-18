# BFD Agora releases

**BFD Agora** is upstream [T3 Code](https://github.com/pingdotgg/t3code) Nightly with
three things changed: the app name, the icon and the update feed. Every other file is
upstream's own, and the app is re-signed with Black Flag's Developer ID. There is no
fork of the source. Its server is upstream's, so the T3 mobile app and linked machines
work with it exactly as they do with upstream T3 Code.

- **Mac:** download the `.dmg` for your chip (`arm64` for Apple Silicon) from the newest
  release in [Releases](https://github.com/black-flag-collective/bfd-t3-releases/releases).
  BFD Agora then updates itself from this feed.

Until notarization is enabled, a release's notes say so. For a first install, run
`xattr -dr com.apple.quarantine "/Applications/BFD Agora.app"` once; updates install normally.

## How a release is made

[`stamp-nightly`](.github/workflows/stamp-nightly.yml) checks upstream every three hours.
For each new nightly it verifies upstream's files against upstream's checksums, stamps
and re-signs the app ([`scripts/stamp-mac.sh`](scripts/stamp-mac.sh)), and confirms that
every other file still matches upstream ([`scripts/compare-bundles.py`](scripts/compare-bundles.py)).
It also starts the stamped app and upstream's CLI of the same version, and refuses to publish
unless both servers report the same version, orchestration protocol and database schema
([`scripts/check-server.sh`](scripts/check-server.sh)). Notarization runs once Apple accepts
the team's key ([`scripts/check-apple-notary.mjs`](scripts/check-apple-notary.mjs)).

## The Agora theme

[`themes/bfd-agora.json`](themes/bfd-agora.json) is the team's T3 theme. Team cloud
computers apply it by themselves whenever this file changes. On a desktop, run:

```sh
curl -fsSL -o /tmp/bfd-agora.json https://raw.githubusercontent.com/black-flag-collective/bfd-t3-releases/main/themes/bfd-agora.json
t3 theme set /tmp/bfd-agora.json
```

Or import the file in **Settings → Appearance**.

The sidebar is an update board with five groups. A thread's title and the app's own status
decide where it sits, never who is looking:

- **Needs a person**: `NEEDS <NAME>: <exact action>` titles, and any thread with a pending
  approval, question or request. Three parts, in this order:
  - **Replies & outbox**: `NEEDS <NAME>: Reply to <person> — <subject>` and
    `NEEDS <NAME>: Approve send — <audience>: <subject>` (also `Send reply to …`).
  - **Answer in thread**: an agent asked something inside the thread and is stopped on it.
  - **Other actions**: every other `NEEDS` title.
- **To read**: `READ: <result>`, for finished work only, with a **Got it** button that settles it.
- **Working**: a turn is running now.
- **Picking back up**: every other open thread. The turn ended, it failed, or its model ran
  out of usage. Agents have it; the row says which.
- **Later**: the app's snoozed shelf.

A thread titled `Sweep · <what the last run did>` is the board's footer: one line, stuck to
the bottom, showing when the sweep last ran. A sweep awaiting an approval, question or request
appears in Needs a person instead, with its row and count. When that thread fails, runs out of usage, or is
retitled `Sweep stopped · <reason>`, the line turns red and moves to the top. The
reason is shown as written. Unsent drafts stay out of every group and count and
sit after the open threads; a group heading past 30 threads reads `30+`.

A title that ends with a middle dot and a first name, as in `READ: Invite sent · Eli`, shows
that person as the one who asked. The top bar repeats the groups with counts. The phone app
shows no theme, so the `NEEDS <NAME>:` and `READ:` prefixes are the whole signal there.
Portraits are embedded in the theme, so a new teammate needs a portrait added to it.
