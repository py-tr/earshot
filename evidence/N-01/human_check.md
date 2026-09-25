# N-01 (WCAG 2.2.2 Pause, Stop, Hide): verification split

- **By ear (Bob, `listen()`)**: the new control is reachable by keyboard and announced by NVDA as "Pause animation, button" (see `ear_check_bob_listen.txt`). This proves the control exists and is named. It does **not** prove the motion stops.
- **By eye (human, 2026-09-25 21:21 CEST)**: on `/flights`, clicking "Pause animation" froze the twinkling and drifting starfield, and the button changed to "Resume animation"; clicking again resumed it. Screen-recorded (kept with the video assets, not in the repo).
- **Not addressed (recommended practice, outside 2.2.2)**: honouring the OS "reduce motion" setting.
