# Sweep a page by ear

- Call listen with key_script "Tab ×25", start "TOP", gap 1.5 and the page path; if it replies "running", call listen_result (never sleep).
- Flag a Tab as suspicious when NVDA says nothing new, says only a role ("link", "button", "edit", "graphic"), reads example or placeholder text as the name, lands on "[page behind dialog]", or gives the same name to different targets.
- Also flag it when the same control is reached on two Tabs in a row (e.g. a button nested inside a link), and when a link's spoken name is a web address such as "github.com" (the link has no text).
- Ignore everything after focus leaves the page (focus shows BODY, or NVDA speaks browser controls such as "Tab search" or "Address and search bar").
