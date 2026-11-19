# Sidebar identity and motion

The client is the subject; Minion is the agent. Preserve the native agent/project image and add the canonical Agora client mark and name when a title explicitly names a known client or internal product. Unknown titles retain their native project label. This does not move workspaces, infer client access, or change permissions. Renaming a title updates its association immediately. Client-specific rules override internal product matches.

Assets come from Agora client records read November 19, 2026. The first release covers BFD infrastructure, PowerAdvice, Healthspan, NCEE, Warrior Week and Trabian. Multi-client and unnamed work still needs native metadata support; do not claim complete inference from CSS.

Active rows use a slow highlight on their state rule. It signals activity without pretending to measure completion; waiting rows remain still. Reduced motion disables the highlight. Keep native status text, hover actions and keyboard focus.

Evaluate on the real Nightly: wide/narrow, light/dark, native hover/focus, running/waiting transitions, settled updates and sweep failure. No new mockup is acceptance evidence.

## Top bar and session desk

The top bar is all reel. It runs from the BFD Agora wordmark to the panel switches at the right end, one headline at a time, with a colored tab for its kind and a line that fills along the bottom of the bar. The open thread's name leaves the bar.

The thread details panel is the session desk. The real breadcrumb is moved in as the title block, so it is still the button that opens thread actions. Below it is the session read slot, then the workspace line, then Git folded into one line at the bottom (branch and diff) that opens on hover or keyboard focus.

The session read is data, not theme. A scorer in minion-keith grades each active thread on five fixed measures (progress, momentum, clarity, risk, on you), writes a verdict and one sentence, and ranks the three most likely next asks. It renders that as dark and light panel images and keys them to the thread with `aside[data-thread-details-panel][data-workspace-focus-key$=":<threadId>"]`, setting `--bfd-desk-img`, `--bfd-desk-ar`, `--bfd-desk-text` and `--bfd-desk-alt`. The keeper appends that layer to this released theme on each machine. A thread with no read shows a quiet placeholder.
