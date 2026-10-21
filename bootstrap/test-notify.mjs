// No model calls or actual notifications. Run with Node 24+.
import assert from 'node:assert/strict';
import notify from '../config/pi/extensions/notify.ts';

const handlers = new Map();
notify({ on: (event, handler) => handlers.set(event, handler) });
assert.deepEqual([...handlers.keys()], ['agent_settled']);
const handler = handlers.get('agent_settled');
const originalWrite = process.stdout.write;
const originalTTY = Object.getOwnPropertyDescriptor(process.stdout, 'isTTY');
const originalKitty = process.env.KITTY_WINDOW_ID;
let output = '';
try {
  process.stdout.write = (text) => { output += text; return true; };
  Object.defineProperty(process.stdout, 'isTTY', { value: true, configurable: true });
  delete process.env.KITTY_WINDOW_ID;
  for (const mode of ['rpc', 'json', 'print']) await handler({}, { mode });
  assert.equal(output, '');
  await handler({}, { mode: 'tui' });
  assert.equal(output, '\x1b]777;notify;🟢 Pi;Ready for input\x07');
  output = '';
  process.env.KITTY_WINDOW_ID = 'test';
  await handler({}, { mode: 'tui' });
  assert.equal(output, '\x1b]99;i=1:d=0;🟢 Pi\x1b\\\x1b]99;i=1:p=body;Ready for input\x1b\\');
  output = '';
  Object.defineProperty(process.stdout, 'isTTY', { value: false, configurable: true });
  await handler({}, { mode: 'tui' });
  assert.equal(output, '');
} finally {
  process.stdout.write = originalWrite;
  if (originalTTY) Object.defineProperty(process.stdout, 'isTTY', originalTTY);
  else delete process.stdout.isTTY;
  if (originalKitty === undefined) delete process.env.KITTY_WINDOW_ID;
  else process.env.KITTY_WINDOW_ID = originalKitty;
}
console.log('PASS: settled-only, OSC 777/99, noninteractive and non-TTY suppression');
