import { createHash, randomBytes } from 'node:crypto';
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { createRequire } from 'node:module';
import { AUTH_URL, SCOPE, exchange, requestJson, validateClient, validateToken } from './core.mjs';

// Reuse the native keyring installed with this workstation's Pi MCP adapter.
// Lazy loading avoids opening Keychain during extension discovery. No file fallback.
export function keychainStore() {
  function entry() {
    if (process.platform !== 'darwin') throw new Error('This local Gmail extension currently requires macOS Keychain');
    try {
      const require = createRequire(join(homedir(), '.pi/agent/npm/package.json'));
      const { Entry } = require('@napi-rs/keyring');
      return new Entry('pi-gmail-readonly', 'google-desktop-v1');
    } catch { throw new Error('Native Keychain support unavailable; check Pi MCP adapter installation. No plaintext fallback.'); }
  }
  return {
    async read() {
      try {
        const value = entry().getPassword();
        if (!value) throw new Error('missing');
        return JSON.parse(value);
      } catch { throw new Error('Gmail Keychain entry is missing, locked, or invalid. Run /gmail-setup or unlock Keychain.'); }
    },
    async write(record) {
      try { entry().setPassword(JSON.stringify(record)); }
      catch { throw new Error('Unable to save Gmail authorization in Keychain. No plaintext fallback.'); }
    },
    async remove() {
      try { if (!entry().deletePassword()) throw new Error('missing'); }
      catch { throw new Error('Unable to remove Gmail Keychain entry (missing or locked)'); }
    },
  };
}

export async function readDesktopClient(path) {
  const expanded = path.startsWith('~/') ? join(homedir(), path.slice(2)) : path;
  const file = resolve(expanded);
  const info = await stat(file);
  if (!info.isFile() || info.size > 64 * 1024) throw new Error('OAuth client must be a regular JSON file under 64 KiB');
  let parsed;
  try { parsed = JSON.parse(await readFile(file, 'utf8')); }
  catch { throw new Error('Unable to parse the selected OAuth client JSON'); }
  return validateClient(parsed);
}

export async function authorize({ client, expectedEmail, open, store, signal, fetcher = fetch }) {
  if (!expectedEmail || !/^[^\s@]+@[^\s@]+$/.test(expectedEmail)) throw new Error('Enter the exact Gmail account email to authorize');
  signal?.throwIfAborted();
  const state = randomBytes(32).toString('base64url');
  const verifier = randomBytes(48).toString('base64url');
  const challenge = createHash('sha256').update(verifier).digest('base64url');
  let accept;
  const callback = new Promise(resolveCallback => { accept = resolveCallback; });
  const server = createServer((req, res) => {
    const url = new URL(req.url ?? '/', 'http://127.0.0.1');
    if (req.method !== 'GET' || url.pathname !== '/oauth/callback') { res.writeHead(404).end(); return; }
    if (url.searchParams.get('state') !== state) { res.writeHead(400).end('State mismatch'); return; }
    const code = url.searchParams.get('code');
    const denied = !!url.searchParams.get('error') || !code;
    res.writeHead(denied ? 400 : 200, { 'content-type': 'text/plain', 'cache-control': 'no-store' });
    res.end(denied ? 'Authorization was not completed.' : 'Authorization response received. Return to Pi to verify completion.');
    accept(denied ? { error: true } : { code });
  });
  let timer;
  const abort = () => accept({ error: true });
  signal?.addEventListener('abort', abort, { once: true });
  try {
    await new Promise((ok, fail) => {
      server.once('error', fail);
      server.listen(0, '127.0.0.1', ok);
    });
    signal?.throwIfAborted();
    const redirect_uri = `http://127.0.0.1:${server.address().port}/oauth/callback`;
    const url = new URL(AUTH_URL);
    url.search = new URLSearchParams({ client_id: client.client_id, redirect_uri, response_type: 'code', scope: SCOPE,
      access_type: 'offline', prompt: 'consent', include_granted_scopes: 'false', login_hint: expectedEmail,
      state, code_challenge: challenge, code_challenge_method: 'S256' }).toString();
    timer = setTimeout(() => accept({ error: true }), 300_000);
    await open(url.toString());
    const outcome = await callback;
    if (outcome.error) throw new Error('Gmail authorization cancelled, denied, or timed out');
    signal?.throwIfAborted();
    const token = validateToken(await exchange(client, { grant_type: 'authorization_code', code: outcome.code, redirect_uri, code_verifier: verifier }, signal, fetcher));
    const profile = await requestJson('https://gmail.googleapis.com/gmail/v1/users/me/profile', {
      method: 'GET', headers: { authorization: `Bearer ${token.access_token}` }, signal,
    }, fetcher);
    if (profile.emailAddress?.toLowerCase() !== expectedEmail.toLowerCase()) {
      throw new Error('Authorized Google account does not match the requested email; authorization not saved');
    }
    await store.write({ version: 1, client, email: profile.emailAddress, token });
    return profile.emailAddress;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
    server.closeAllConnections();
    await new Promise(resolveClose => server.close(resolveClose));
  }
}
