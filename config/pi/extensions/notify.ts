/**
 * Terminal-only adaptation of Pi's MIT-licensed notification example.
 * Source revision and attribution: docs/extensions.md; license: notify.LICENSE.
 * Local changes: interactive/TTY guard, fixed title, no Windows toast support.
 * Only static readiness text is emitted; never prompt or response content.
 */
import type { ExtensionAPI } from '@earendil-works/pi-coding-agent';

function notifyOSC777(title: string, body: string): void {
  process.stdout.write(`\x1b]777;notify;${title};${body}\x07`);
}

function notifyOSC99(title: string, body: string): void {
  process.stdout.write(`\x1b]99;i=1:d=0;${title}\x1b\\`);
  process.stdout.write(`\x1b]99;i=1:p=body;${body}\x1b\\`);
}

export default function (pi: ExtensionAPI) {
  pi.on('agent_settled', async (_event, ctx) => {
    if (ctx.mode !== 'tui' || !process.stdout.isTTY) return;
    const notify = process.env.KITTY_WINDOW_ID ? notifyOSC99 : notifyOSC777;
    notify('🟢 Pi', 'Ready for input');
  });
}
