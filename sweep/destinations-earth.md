# Sweep — /destinations/earth

Tab ×25 from TOP, gap 1.5 s, NVDA.

| Stop | Focus | NVDA said |
|------|-------|-----------|
| 1 | Skip to main content (link) | "clickable, Skip to main content, same page, link" |
| 2 | Pause animation (button) | "Pause animation, button" |
| 3 | Galaxium Travels (link, banner) | "banner landmark, Galaxium Travels, link" |
| 4 | Home (link, nav) | "navigation landmark, Home, link" |
| 5 | Flights (link) | "Flights, link" |
| 6 | Login (button) | "Login, button" |
| 7 | All Destinations (link, main) | "main landmark, All Destinations, link" |
| 8 | Book Mars to Earth, Jan 03, 2099 (link) | "Book Mars to Earth, Jan 03, 2099, link" |
| 9 | Book Venus to Earth, Jan 04, 2099 (link) | "Book Venus to Earth, Jan 04, 2099, link" |
| 10 | Book Europa to Earth, Jan 09, 2099 (link) | "Book Europa to Earth, Jan 09, 2099, link" |
| 11 | GitHub (link, footer) | "content info landmark, GitHub, link" |
| — | BODY | focus left page |

## Proposed findings

S-01 | /destinations/earth | Tab ×11 | "content info landmark, GitHub, link" | Icon-only link in footer has `aria-label="GitHub"` — bare brand name gives no context about destination or purpose | "Galaxium on GitHub, link" | `galaxium/booking_system_frontend/src/components/layout/Footer.tsx:29`
