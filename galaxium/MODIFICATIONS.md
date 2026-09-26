# Modifications to Galaxium Travels (Apache License 2.0, section 4(b) notice)

`galaxium/` is derived from IBM's sample app **IBM/galaxium-travels**, commit `e4e18ae`, licensed under the Apache License 2.0 (see `LICENSE` in this folder). This copy was modified for the Earshot project during the IBM Bob 2.0 Hackathon (25–27 September 2026).

## Not included from upstream
`.bob/` (IBM's Bob modes, hooks, skills, settings), `AGENTS.md`, `.github/`, `booking_system_inventory_hold_service/` (Java), `demos/`, `e2e/`, `scripts/`, `docker-compose.yml`, `start.sh`, `test.sh`. Only `booking_system_frontend/`, `booking_system_backend/`, `LICENSE` and `README.md` were copied.

## Changed files
Each accessibility fix was written by IBM Bob in an Earshot `/hear` task and verified with the NVDA screen reader; see the root `findings.md`, `evidence/`, and `bob_sessions/`.

| File | Change | Finding |
|---|---|---|
| `booking_system_frontend/src/components/common/Modal.tsx` | the dialog gets an accessible name, focus moves into it on open, focus is trapped inside, and focus returns to the opener on close | F-01, F-02 |
| `booking_system_frontend/src/components/common/Input.tsx` | the label is associated with its input (`useId`, `htmlFor`) | F-03 |
| `booking_system_frontend/src/components/common/Starfield.tsx` | Pause/Resume control for the background animation | N-01 |
| `booking_system_frontend/src/components/common/Button.tsx` | forwards `aria-label` | F-04 |
| `booking_system_frontend/src/components/flights/FlightCard.tsx` | booking buttons name their route ("Select Seat Class, Earth to Mars") | F-04 |
| `booking_system_frontend/src/components/layout/Layout.tsx` | "Skip to main content" link; `id="main-content"` on `<main>` | F-05 |
| `booking_system_frontend/src/pages/Flights.tsx` | search field named "Search flights" | F-06 |
| `booking_system_frontend/src/components/layout/Header.tsx` | "Book a Flight" is one styled link instead of a button nested inside a link | F-07 |
| `booking_system_frontend/src/pages/Home.tsx` | "Explore Flights" and "Book Your Flight Now" are styled links instead of buttons nested inside links | F-07 |
| `booking_system_backend/requirements.txt` | pinned `fastmcp==2.14.7` and `mcp==1.30.0` (unpinned versions crash `FastApiMCP` on a fresh install) | setup |
