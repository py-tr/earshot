# Upstream

This folder is [Uptime Kuma](https://github.com/louislam/uptime-kuma) at tag `2.5.5` (commit `c98982a`), MIT licence (see `LICENSE`), vendored unmodified as Earshot's third app: a self-hosted monitoring tool that people run in production.

Changes made for Earshot come after the vendoring commit, each as its own commit, and are listed below.

## Changes

All in `src/`, each written by IBM Bob and verified by ear with NVDA (commits in this repo):

- `layouts/Layout.vue`: the two logo `<object>` elements get `aria-hidden="true" tabindex="-1"`, so they are no longer a silent Tab stop (F-13, ead8170).
- `components/HeartbeatBar.vue`: new `inLink` prop. Inside a link the canvas is `aria-hidden` and not focusable, and a visually hidden span puts the heartbeat summary into the link's name; elsewhere the canvas keeps `role="img"`, its label, `tabindex="0"` and the arrow-key handlers (F-14 012cd1b, c3bd27d, b52c1f7).
- `components/MonitorListItem.vue`: passes `:in-link="true"` to both heartbeat bars (F-14, c3bd27d).
