# Sidebar identity and motion

The client is the subject; Minion is the agent. Preserve the native agent/project image and add the canonical Agora client mark and name when a title explicitly names a known client or internal product. Unknown titles retain their native project label. This does not move workspaces, infer client access, or change permissions. Renaming a title updates its association immediately. Client-specific rules override internal product matches.

Assets come from Agora client records read November 19, 2026. The first release covers BFD infrastructure, PowerAdvice, Healthspan, NCEE, Warrior Week and Trabian. Titles matching multiple client families retain native project metadata; aliases within one family still resolve to that client. Internal product matches never override a single named client. Unnamed work also retains native metadata; do not claim complete inference from CSS.

Active rows use a slow highlight on their state rule. It signals activity without pretending to measure completion; waiting rows remain still. Reduced motion disables the highlight. Keep native status text, hover actions and keyboard focus.

Evaluate on the real Nightly: wide/narrow, light/dark, native hover/focus, running/waiting transitions, settled updates and failed/limited automation runs. No new mockup is acceptance evidence.

Section order: Needs Keith / Needs action, Updates, Working, Automations, Open threads, Later.
Finished work uses `UPDATE: <result>`; `READ:` has no special styling. Scheduled jobs use
`AUTOMATION: <plain name>` and settle after each run. Automation rows stay compact and
use a muted dot; Failed and Limited turn red without moving out of Automations.
