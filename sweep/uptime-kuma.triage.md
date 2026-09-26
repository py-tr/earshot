# Triage: Uptime Kuma dashboard sweep (task46, `/earshot http://localhost:3000/dashboard`)

Human decisions on Bob's 8 proposals in [uptime-kuma.md](uptime-kuma.md):

| Proposal | Decision | Finding |
|---|---|---|
| S-01 silent Tab stop on the logo `<object>` | accepted, with the expected announcement rewritten by the human ("Status Pages, link" on the second Tab) | F-13 |
| S-02..S-07 status filters read as "clickable, Up2" (count glued to the label, `div` with no button role) | **deferred, not rejected**: real, one bug with six instances; left out of this run to keep it short. Bob's summary lists them as "rejected"; the human decision was to defer. Listed under Known issues. | none yet |
| S-08 heartbeat canvas: a second Tab stop inside each monitor link ("graphic, clickable, link") | accepted, expected announcement rewritten by the human (the Tab after "Galaxium ... link" goes straight to "TodoMVC ... link") | F-14 |
