#!/bin/bash
# Launch the stamped app and upstream's own CLI of the same version, each in a throwaway home, and
# require their servers to report the same version, orchestration protocol and database schema.
# Mobile clients and linked machines talk to that server, so a match means they keep working.
#
# usage: check-server.sh <stamped.app> <upstream-cli-dir-containing-t3>
set -euo pipefail
app=$1; cli=$2
work=$(mktemp -d)
pids=()
cleanup() {
  for pid in "${pids[@]}"; do
    pkill -TERM -P "$pid" 2>/dev/null || true
    kill -TERM "$pid" 2>/dev/null || true
  done
  rm -rf "$work"
}
trap cleanup EXIT

descriptor() { curl -sf -m 3 "http://127.0.0.1:$1/.well-known/t3/environment"; }
fields() { python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["serverVersion"], d["orchestrationProtocolVersion"], d["databaseMigration"])'; }

mkdir -p "$work/cli-home"
T3CODE_HOME="$work/cli-home" "$cli/t3" --host 127.0.0.1 --port 39981 --no-browser > "$work/cli.log" 2>&1 &
pids+=($!)
for _ in $(seq 1 90); do descriptor 39981 > "$work/upstream.json" && break; sleep 2; done
[ -s "$work/upstream.json" ] || { tail -20 "$work/cli.log"; echo "upstream CLI never answered" >&2; exit 1; }
upstream=$(fields < "$work/upstream.json")

exe="$app/Contents/MacOS/$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$app/Contents/Info.plist")"
mkdir -p "$work/app-home"
HOME="$work/app-home" "$exe" > "$work/app.log" 2>&1 &
app_pid=$!
pids+=("$app_pid")
stamped=""
for _ in $(seq 1 90); do
  # The desktop's server runs a few processes below the app, so try every new listener.
  for port in $(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk 'NR>1 {sub(/.*:/, "", $9); print $9}' | sort -u); do
    [ "$port" = 39981 ] && continue
    if body=$(descriptor "$port"); then stamped=$(printf '%s' "$body" | fields); break 2; fi
  done
  sleep 2
done
[ -n "$stamped" ] || { tail -40 "$work/app.log"; echo "stamped app's server never answered" >&2; exit 1; }

echo "upstream CLI server: $upstream"
echo "stamped app server:  $stamped"
[ "$upstream" = "$stamped" ] || { echo "server mismatch" >&2; exit 1; }
