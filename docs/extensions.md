# Extension provenance

These files are local adaptations, not automatic installations or updates of upstream packages. Keep the accompanying license notices when redistributing them. No blanket license is granted for unrelated repository content.

## Read-only Gmail

`config/pi/extensions/gmail-readonly/` is a local implementation informed by [guquan-2002/pi-gmail](https://github.com/guquan-2002/pi-gmail/tree/e52449ee9dbd2e585bdd0df18c18526d65acdc6d), reviewed at revision `e52449ee9dbd2e585bdd0df18c18526d65acdc6d` (upstream package 1.0.1). The upstream npm package is not installed by this repository.

The upstream [MIT license](https://github.com/guquan-2002/pi-gmail/blob/e52449ee9dbd2e585bdd0df18c18526d65acdc6d/LICENSE), copyright 2026 guquan, is retained at `config/pi/extensions/gmail-readonly/LICENSE`. The notice was checked against that exact public revision before this release. This is attribution of the implementation's source influence, not a claim that the files are an unmodified upstream copy.

Local behavior includes fixed read-only Gmail scope, account confirmation, macOS Keychain storage, bounded responses and attachment/body completeness reporting. Authentication records, Desktop client files, mailbox content and session logs are not included. Runtime compatibility still depends on the installed Pi/Node environment described in the README.

## Terminal notifications

`config/pi/extensions/notify.ts` is adapted from Pi's [notification example](https://github.com/earendil-works/pi/blob/02726086d11c2911aa872959e308b90d69182392/packages/coding-agent/examples/extensions/notify.ts) at revision `02726086d11c2911aa872959e308b90d69182392`. The accompanying [MIT license](https://github.com/earendil-works/pi/blob/02726086d11c2911aa872959e308b90d69182392/LICENSE), copyright 2025 Mario Zechner, is retained in `config/pi/extensions/notify.LICENSE`.

Before publication, the prior mixed-source adapter was replaced with an adaptation of this identified, permissively licensed example. The OSC helper functions come from Pi; local changes require interactive TUI mode and a terminal stdout, use a fixed readiness title, and omit Windows toast execution. No conversation text is emitted. Tests mock stdout and do not send real notifications.
