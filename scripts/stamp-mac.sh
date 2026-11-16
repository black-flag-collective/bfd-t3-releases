#!/bin/bash
# Stamp one upstream T3 Code macOS app as BFD Agora. Only the name, icon and update feed change;
# every other byte stays upstream's, then the bundle is re-signed with Black Flag's Developer ID.
#
# usage: stamp-mac.sh <upstream-app-zip> <out-dir> <arch>
# env:   SIGN_IDENTITY  Developer ID Application identity in the unlocked build keychain
#        TEAM_ID        Black Flag's Apple team ID
#        ICNS           BFD Agora .icns
set -euo pipefail

zip=$1; out=$2; arch=$3
: "${SIGN_IDENTITY:?}" "${TEAM_ID:?}" "${ICNS:?}"
NAME="BFD Agora"
FEED_OWNER=black-flag-collective
FEED_REPO=bfd-t3-releases

work=$(mktemp -d)
ditto -x -k "$zip" "$work/upstream"
src=$(find "$work/upstream" -maxdepth 1 -name '*.app' | head -1)
[ -n "$src" ] || { echo "No app in $zip" >&2; exit 1; }
mkdir -p "$out"
app="$out/$NAME.app"
rm -rf "$app"
ditto "$src" "$app"

plist="$app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleName $NAME" "$plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $NAME" "$plist"
/usr/libexec/PlistBuddy -c "Set :ElectronTeamID $TEAM_ID" "$plist"
# An asset-catalog icon would win over icon.icns.
/usr/libexec/PlistBuddy -c "Delete :CFBundleIconName" "$plist" 2>/dev/null || true
icon=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIconFile" "$plist")
cp "$ICNS" "$app/Contents/Resources/${icon%.icns}.icns"

feed="$app/Contents/Resources/app-update.yml"
grep -q '^provider: github$' "$feed" || { echo "Unexpected update feed:" >&2; cat "$feed" >&2; exit 1; }
sed -i '' -e "s/^owner: .*/owner: $FEED_OWNER/" -e "s/^repo: .*/repo: $FEED_REPO/" "$feed"

# Upstream's provisioning profile and passkey entitlements belong to its Apple team. A Developer ID
# app without the matching profile is killed at launch, so both go; T3 Connect falls back to the
# browser sign-in.
rm -f "$app/Contents/embedded.provisionprofile"

entitlements_for() {
  local target=$1 file=$2
  codesign -d --entitlements :- "$target" 2>/dev/null > "$file.raw" || true
  if [ ! -s "$file.raw" ]; then
    rm -f "$file.raw"
    return 1
  fi
  python3 - "$file.raw" "$file" <<'PY'
import plistlib, sys
data = plistlib.load(open(sys.argv[1], 'rb'))
for key in list(data):
    if (key.startswith('com.apple.developer.') or key in (
            'com.apple.application-identifier', 'keychain-access-groups')):
        del data[key]
plistlib.dump(data, open(sys.argv[2], 'wb'))
PY
  rm -f "$file.raw"
}

sign() {
  local target=$1 ent="$work/ent.plist"
  if entitlements_for "$target" "$ent"; then
    codesign --force --timestamp --options runtime --entitlements "$ent" --sign "$SIGN_IDENTITY" "$target"
  else
    codesign --force --timestamp --options runtime --sign "$SIGN_IDENTITY" "$target"
  fi
}

# Inside out: loose Mach-O files, then nested bundles deepest first, then the app.
while IFS= read -r -d '' file; do
  if file -b "$file" | grep -q 'Mach-O'; then
    sign "$file"
  fi
done < <(find "$app/Contents" -type f \( -perm -u+x -o -name '*.dylib' -o -name '*.node' -o -name '*.so' \) -print0)
while IFS= read -r bundle; do
  sign "$bundle"
done < <(find "$app/Contents" -depth -type d \( -name '*.app' -o -name '*.framework' -o -name '*.xpc' \) | awk '{ print length, $0 }' | sort -rn | cut -d' ' -f2-)
sign "$app"

codesign --verify --deep --strict --verbose=2 "$app"
codesign -dv "$app" 2>&1 | grep -E "^(Identifier|TeamIdentifier)="
rm -rf "$work"
echo "$app"
