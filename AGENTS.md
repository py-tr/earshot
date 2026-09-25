galaxium/ is third-party (Apache-2.0); only its frontend src is edited, exclusively via the earshot mode.
Accessibility findings are listed in findings.md.
A fix counts as verified only when earshot listen() output contains the expected NVDA announcement.
Never read files under takes/, or any *.log or *.wav file.
All other files in this repo are read-only for the earshot mode.
