// Synthetic fixtures only. No real Google requests, Keychain access, or mailbox data.
import assert from 'node:assert/strict';
import test from 'node:test';
import { createRequire } from 'node:module';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { SCOPE, AUTH_URL, TOKEN_URL, validateClient, validateToken, createClient, search, message, thread, outputPage, requestJson } from '../config/pi/extensions/gmail-readonly/core.mjs';
import { authorize } from '../config/pi/extensions/gmail-readonly/oauth.mjs';

const credentials = { client_id: 'synthetic.apps.googleusercontent.com', client_secret: 'test-only' };
const token = () => ({ access_token: 'test-access', refresh_token: 'test-refresh', scope: SCOPE, expiry_date: Date.now() + 3600_000 });
const rawToken = () => ({ access_token: 'test-access', refresh_token: 'test-refresh', scope: SCOPE, expires_in: 3600 });
const response = value => new Response(JSON.stringify(value), { status: 200 });
const payload = text => ({ mimeType: 'text/plain', body: { data: Buffer.from(text).toString('base64url') } });
function memoryStore(t = token()) {
  let record = { version: 1, client: credentials, email: 'reader@example.test', token: t };
  return { read: async () => record, write: async next => { record = next; } };
}

test('Google endpoint validation and strictly read-only scopes', () => {
  assert.deepEqual(validateClient({ installed: { ...credentials, auth_uri: AUTH_URL, token_uri: TOKEN_URL } }), credentials);
  for (const url of ['https://evil.example/token', 'http://oauth2.googleapis.com/token', TOKEN_URL + '?extra=1']) {
    assert.throws(() => validateClient({ installed: { ...credentials, auth_uri: AUTH_URL, token_uri: url } }));
  }
  for (const scope of [undefined, SCOPE + ' https://www.googleapis.com/auth/gmail.send', 'https://mail.google.com/']) {
    assert.throws(() => validateToken({ ...rawToken(), scope }));
  }
  assert.equal(validateToken(rawToken()).scope, SCOPE);
  assert.equal(validateToken({ access_token: 'new', expires_in: 3600 }, token()).refresh_token, 'test-refresh');
});

test('fixed origin, GET-only transport, no redirects; bad paths fail before network', async () => {
  const calls = [];
  const client = createClient(memoryStore(), async (url, init) => { calls.push({ url, init }); return response({}); });
  await client.get('/profile');
  assert.equal(calls[0].url, 'https://gmail.googleapis.com/gmail/v1/users/me/profile');
  assert.equal(calls[0].init.method, 'GET');
  assert.equal(calls[0].init.redirect, 'error');
  for (const path of ['https://evil.example', '//evil.example', '/messages/abc/trash', '/messages/../profile', '/settings', '/profile#x']) {
    await assert.rejects(() => client.get(path));
  }
  assert.equal(calls.length, 1);
});

test('refresh stays read-only, persists, and coalesces concurrent requests', async () => {
  let exchanges = 0;
  const store = memoryStore({ ...token(), expiry_date: 0 });
  const client = createClient(store, async (url, init) => {
    if (url === TOKEN_URL) {
      exchanges++;
      assert.equal(init.redirect, 'error');
      assert.equal(init.body.get('grant_type'), 'refresh_token');
      await new Promise(resolve => setTimeout(resolve, 5));
      return response({ access_token: 'renewed', expires_in: 3600 });
    }
    return response({});
  });
  await Promise.all([client.get('/profile'), client.get('/profile')]);
  assert.equal(exchanges, 1);
  assert.equal((await store.read()).token.access_token, 'renewed');
});

test('search exposes nextPageToken and forwards it; blank queries rejected', async () => {
  const urls = [];
  const client = { get: async path => {
    urls.push(path);
    return path.startsWith('/messages?') ? { messages: [{ id: 'abc' }], nextPageToken: 'page2' }
      : { id: 'abc', threadId: 'def', payload: { headers: [{ name: 'From', value: 'sender@example.test' }] } };
  } };
  const found = await search(client, { query: 'from:example.test', pageToken: 'page1' });
  assert.equal(found.nextPageToken, 'page2');
  assert.equal(found.complete, false);
  assert.match(urls[0], /pageToken=page1/);
  await assert.rejects(() => search(client, { query: ' ' }));
});

test('attachment-backed body fetched; documents listed, not blended into body', async () => {
  const urls = [];
  const client = { get: async path => {
    urls.push(path);
    if (path.includes('/attachments/')) return { data: Buffer.from('Actual body').toString('base64url') };
    return { id: 'abc', threadId: 'def', payload: { mimeType: 'multipart/mixed', parts: [
      { mimeType: 'text/plain', body: { attachmentId: 'part1', size: 11 } },
      { ...payload('NOT BODY'), filename: 'notes.txt' },
    ] } };
  } };
  const m = await message(client, 'abc');
  assert.equal(m.body, 'Actual body');
  assert.equal(m.attachments.length, 1);
  assert.equal(m.contentComplete, false);
  assert.equal(urls.length, 2);
});

test('thread includes all messages; HTML, missing bodies and unsupported MIME disclose limitations', async () => {
  const client = { get: async () => ({ id: 'def', messages: [
    { id: 'abc', payload: payload('first') },
    { id: 'def', payload: { mimeType: 'text/html', body: { data: Buffer.from('<p>second</p>').toString('base64url') } } },
    { id: 'ghi', payload: { mimeType: 'application/pkcs7-mime' } },
  ] }) };
  const t = await thread(client, 'def');
  assert.equal(t.messages.length, 3);
  assert.match(t.messages[1].body, /second/);
  assert.equal(t.contentComplete, false);
  assert.ok(t.messages[2].warnings.length);
});

test('non-UTF-8 charset is explicitly uncertain; decode failures are incomplete', async () => {
  const client = { get: async () => ({ id: 'abc', payload: {
    ...payload('café'), headers: [{ name: 'Content-Type', value: 'text/plain; charset=windows-1252' }],
  } }) };
  const m = await message(client, 'abc');
  assert.equal(m.contentComplete, false);
  assert.match(m.warnings.join(' '), /verify text fidelity/);
  const bad = await message({ get: async () => ({ id: 'abc', payload: {
    mimeType: 'text/plain', body: { data: Buffer.from([0xff]).toString('base64url') },
  } }) }, 'abc');
  assert.equal(bad.contentComplete, false);
  assert.match(bad.warnings.join(' '), /could not be decoded/);
});

test('output can be completely reconstructed without disk spills; each envelope is bounded', () => {
  const fixture = { text: ('\u0001\n😀').repeat(12_000) };
  let offset = 0, reconstructed = '', hash;
  do {
    const r = outputPage(fixture, offset);
    assert.ok(Buffer.byteLength(r.content[0].text) < 50 * 1024);
    const p = JSON.parse(r.content[0].text);
    if (hash) assert.equal(p.sha256, hash);
    hash = p.sha256;
    reconstructed += p.data;
    offset = p.nextOffset;
  } while (offset !== null);
  assert.deepEqual(JSON.parse(reconstructed), fixture);
});

test('HTTP failures redact response bodies and oversized responses fail explicitly', async () => {
  await assert.rejects(() => requestJson('https://example.test', {}, async () => new Response('secret-private-body', { status: 401 })), error => !error.message.includes('secret-private-body') && error.message.includes('401'));
  await assert.rejects(() => requestJson('https://example.test', {}, async () => new Response('x'.repeat(12 * 1024 * 1024 + 1))), /exceeds/);
});

async function authFixture(expectedEmail, callbackMode = 'valid', override = {}) {
  let saved, authorizeUrl, tokenParams;
  const fetcher = async (url, init) => {
    if (url === TOKEN_URL) { tokenParams = init.body; return response(rawToken()); }
    return response({ emailAddress: 'reader@example.test' });
  };
  const task = authorize({ client: credentials, expectedEmail, store: { write: async r => { saved = r; } }, fetcher,
    open: async url => {
      authorizeUrl = new URL(url);
      const callback = new URL(authorizeUrl.searchParams.get('redirect_uri'));
      callback.searchParams.set('state', 'wrong');
      assert.equal((await fetch(callback)).status, 400);
      callback.searchParams.set('state', authorizeUrl.searchParams.get('state'));
      callback.searchParams.set(callbackMode === 'denied' ? 'error' : 'code', callbackMode === 'denied' ? 'access_denied' : 'synthetic-code');
      await fetch(callback);
    }, ...override,
  });
  await task;
  return { saved, authorizeUrl, tokenParams };
}
test('OAuth uses PKCE/state, accepts only correct account, saves only after live profile', async () => {
  const { saved, authorizeUrl, tokenParams } = await authFixture('reader@example.test');
  assert.equal(saved.email, 'reader@example.test');
  assert.equal(authorizeUrl.searchParams.get('scope'), SCOPE);
  assert.equal(authorizeUrl.searchParams.get('include_granted_scopes'), 'false');
  assert.equal(authorizeUrl.searchParams.get('code_challenge_method'), 'S256');
  assert.equal(createHash('sha256').update(tokenParams.get('code_verifier')).digest('base64url'), authorizeUrl.searchParams.get('code_challenge'));
  await assert.rejects(() => authFixture('wrong@example.test'), /does not match/);
  await assert.rejects(() => authFixture('reader@example.test', 'denied'), /cancelled/);
});

test('shutdown abort closes OAuth listener without storing authorization', async () => {
  const controller = new AbortController();
  let callback;
  await assert.rejects(() => authorize({ client: credentials, expectedEmail: 'reader@example.test', signal: controller.signal,
    store: { write: async () => assert.fail('must not save') }, fetcher: async () => assert.fail('must not exchange'),
    open: async url => { callback = new URL(url).searchParams.get('redirect_uri'); controller.abort(); },
  }), /cancelled|abort/i);
  await assert.rejects(() => fetch(callback));
});

test('extension loads with installed TypeBox; exactly three read tools, no startup network', async () => {
  const require = createRequire(join(homedir(), '.pi/agent/npm/package.json'));
  const { createJiti } = require('jiti');
  const jiti = createJiti(import.meta.url, { alias: { typebox: require.resolve('typebox') } });
  const extension = await jiti.import('../config/pi/extensions/gmail-readonly/index.ts', { default: true });
  const tools = [], commands = [], events = [];
  extension({ registerTool: t => tools.push(t), registerCommand: (n, c) => commands.push([n, c]), on: (n, h) => events.push([n, h]) });
  assert.deepEqual(tools.map(t => t.name), ['gmail_search', 'gmail_get', 'gmail_thread']);
  assert.ok(tools.every(t => t.executionMode === 'sequential'));
  assert.deepEqual(commands.map(([n]) => n), ['gmail-setup', 'gmail-status', 'gmail-logout']);
  assert.equal(events[0][0], 'session_shutdown');
  await assert.rejects(() => commands[0][1].handler('', { hasUI: false }), /interactive/);
  // Merely resolve the dependency. Do not instantiate Entry or access real Keychain.
  assert.ok(require.resolve('@napi-rs/keyring'));
  const source = await readFile(new URL('../config/pi/extensions/gmail-readonly/core.mjs', import.meta.url), 'utf8');
  assert.ok(!source.includes('/messages/send'));
});
