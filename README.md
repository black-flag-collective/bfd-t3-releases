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
