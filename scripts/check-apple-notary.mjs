#!/usr/bin/env node
// Ask Apple's notary service whether it accepts this team's API key before notarizing.
// Apple refuses while the developer account has an agreement waiting. Reads APPLE_API_KEY (the .p8 text), APPLE_API_KEY_ID and APPLE_API_ISSUER; uploads nothing.
import * as NodeCrypto from "node:crypto";

const NOTARY_URL = "https://appstoreconnect.apple.com/notary/v2/submissions";

export function notaryToken({ key, keyId, issuer, now = Date.now() }) {
  const encode = (value) => Buffer.from(JSON.stringify(value)).toString("base64url");
  const issuedAt = Math.floor(now / 1000);
  const signed = `${encode({ alg: "ES256", kid: keyId, typ: "JWT" })}.${encode({
    iss: issuer,
    iat: issuedAt,
    exp: issuedAt + 300,
    aud: "appstoreconnect-v1",
  })}`;
  const signature = NodeCrypto.sign("sha256", Buffer.from(signed), {
    key,
    dsaEncoding: "ieee-p1363",
  });
  return `${signed}.${signature.toString("base64url")}`;
}

/** What a notary answer means for the release: `ok`, or the one thing to do about it. */
export function notaryVerdict(status, body) {
  if (status >= 200 && status < 300)
    return { ok: true, message: "Apple's notary service accepts this key." };
  let code = "";
  let title = "";
  try {
    const error = JSON.parse(body).errors?.[0];
    code = String(error?.code ?? "");
    title = String(error?.title ?? "");
  } catch {
    // Not JSON: report the status alone.
  }
  if (status === 403 && code.includes("AGREEMENT")) {
    return {
      ok: false,
      message:
        "Apple will not notarize for this team until the account holder accepts the current " +
        "Apple Developer agreement. Sign in at https://developer.apple.com/account as the " +
        "account holder, accept the agreement shown there, then rerun this release.",
    };
  }
  if (status === 401) {
    return {
      ok: false,
      message:
        "Apple rejected the notary API key. Check APPLE_API_KEY, APPLE_API_KEY_ID and " +
        "APPLE_API_ISSUER against the Agora Apple Signing item in BFD Automation.",
    };
  }
  if (status >= 400 && status < 500) {
    return {
      ok: false,
      message: `Apple's notary service refused this key: ${status} ${title || code}`.trim(),
    };
  }
  // Apple's own outage is not ours to fail on; notarization itself decides later.
  return { ok: true, message: `Apple's notary service answered ${status}; continuing.` };
}

async function main() {
  const { APPLE_API_KEY: key, APPLE_API_KEY_ID: keyId, APPLE_API_ISSUER: issuer } = process.env;
  if (!key || !keyId || !issuer) {
    console.error("::error::APPLE_API_KEY, APPLE_API_KEY_ID and APPLE_API_ISSUER are required.");
    process.exit(1);
  }
  let token;
  try {
    token = notaryToken({ key, keyId, issuer });
  } catch {
    // A key that cannot sign would only fail later, on the Mac runner.
    console.error("::error::APPLE_API_KEY is not a usable private key (.p8 text).");
    process.exit(1);
  }
  let verdict;
  try {
    const response = await fetch(NOTARY_URL, {
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(30_000),
    });
    verdict = notaryVerdict(response.status, await response.text());
  } catch (error) {
    verdict = {
      ok: true,
      message: `Could not reach Apple's notary service (${error.name}); continuing.`,
    };
  }
  console.log(
    verdict.ok
      ? verdict.message
      : `::error title=Apple notarization is blocked::${verdict.message}`,
  );
  process.exit(verdict.ok ? 0 : 1);
}

if (import.meta.url === `file://${process.argv[1]}`) await main();
