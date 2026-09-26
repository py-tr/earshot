/* global EARSHOT_DATA */
var EARSHOT_DATA = [
  {
    id: "F-01",
    status: "verified",
    wcag: "4.1.2 Name, Role, Value (A); 2.4.3 Focus Order (A)",
    component: "Sign In dialog",
    script: "ENTER → TAB",
    expected: "\u201cSign In, dialog\u201d, then \u201cClose modal, button\u201d",
    audio: {
      before: "../evidence/F-01/before_bob_listen.wav",
      after:  "../evidence/F-01/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "ENTER \u2192 (silence \u2014 focus remains on page behind dialog)",
        "TAB \u2192 Moon, link, heading, level 3"
      ],
      after: [
        "ENTER \u2192 Sign In, dialog",
        "TAB \u2192 Close modal, button"
      ]
    }
  },
  {
    id: "F-02",
    status: "verified",
    wcag: "2.4.3 Focus Order (A)",
    component: "Sign In dialog",
    script: "ENTER, TAB ×6, SHIFT+TAB, ESCAPE",
    expected: "Tab after \u201cRegister\u201d wraps to \u201cClose modal, button\u201d. After Escape: \u201cSelect Seat Class, button\u201d.",
    audio: {
      rejected: "../evidence/F-02/attempt1_rejected_bob_listen.wav",
      after:    "../evidence/F-02/after_bob_listen.wav"
    },
    transcript: {
      rejected: [
        "TAB after Register \u2192 github.com, link (escaped the dialog)"
      ],
      after: [
        "TAB after Register \u2192 Close modal, button",
        "ESCAPE \u2192 Select Seat Class, button"
      ]
    }
  },
  {
    id: "F-03",
    status: "verified",
    wcag: "1.3.1 Info and Relationships (A); 4.1.2 Name, Role, Value (A)",
    component: "Sign In form fields",
    script: "ENTER, TAB, TAB, TAB",
    expected: "\u201cClose modal, button\u201d, then \u201cName, edit\u201d, then \u201cEmail, edit\u201d",
    audio: {
      before: "../evidence/F-03/before_bob_listen_from_F02_run.wav",
      after:  "../evidence/F-03/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB \u2192 John Doe, edit, required"
      ],
      after: [
        "TAB \u2192 Name, edit, required",
        "TAB \u2192 Email, edit, required"
      ]
    }
  },
  {
    id: "F-04",
    status: "verified \u2014 discovered by Bob\u2019s /sweep, accepted by a human",
    wcag: "2.4.6 Headings and Labels (AA); 1.3.1 Info and Relationships (A)",
    component: "/flights booking buttons",
    script: "TAB",
    expected: "\u201cSelect Seat Class, Earth to Mars, button\u201d",
    audio: {
      rejected: "../evidence/F-04/attempt1_rejected_bob_listen.wav",
      after:    "../evidence/F-04/after_bob_listen.wav"
    },
    transcript: {
      rejected: [
        "TAB \u2192 Select Seat Class, button (route missing: Button dropped aria-label)"
      ],
      after: [
        "TAB \u2192 Select Seat Class, Earth to Mars, button"
      ]
    }
  },
  {
    id: "F-05",
    status: "verified \u2014 discovered by Bob\u2019s /sweep, accepted by a human",
    wcag: "2.4.1 Bypass Blocks (A)",
    component: "Every page (no skip link)",
    script: "TAB, ENTER, TAB from top of /flights",
    expected: "\u201cSkip to main content, same page, link\u201d as first tab stop; Enter moves focus into main",
    audio: {
      before: "../evidence/F-05/before_probe_listen.wav",
      after:  "../evidence/F-05/after_skip_focus_listen.wav"
    },
    transcript: {
      before: [
        "first TAB \u2192 Pause animation, button (no skip link)"
      ],
      after: [
        "first TAB \u2192 Skip to main content, same page, link",
        "ENTER \u2192 main landmark, heading, level 1, Available Flights",
        "TAB \u2192 Search flights, edit (header skipped)"
      ]
    }
  },
  {
    id: "F-06",
    status: "verified \u2014 discovered by Bob\u2019s /sweep, accepted by a human",
    wcag: "1.3.1 Info and Relationships (A); 4.1.2 Name, Role, Value (A); 3.3.2 Labels or Instructions (A)",
    component: "/flights search field",
    script: "TAB",
    expected: "\u201cSearch flights, edit\u201d",
    audio: {
      before: "../evidence/F-06/before_bob_sweep_listen.wav",
      after:  "../evidence/F-06/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB \u2192 Search by origin or destination..., edit (placeholder as name)"
      ],
      after: [
        "TAB \u2192 Search flights, edit"
      ]
    }
  },
  {
    id: "F-07",
    status: "verified — discovered by Bob’s /sweep, accepted by a human",
    wcag: "4.1.2 Name, Role, Value (A); 2.4.3 Focus Order (A)",
    component: "Home page: a button nested inside a link, in 3 places (Book a Flight, Explore Flights, Book Your Flight Now)",
    script: "TAB ×17 from top of /",
    expected: "Each control is one Tab stop: “Book a Flight, link” once; never “button, link”",
    audio: {
      before:   "../evidence/F-07/before_bob_sweep_listen.wav",
      rejected: "../evidence/F-07/attempt1_rejected_bob_listen.wav",
      after:    "../evidence/F-07/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB → Book a Flight, button, link",
        "TAB → Book a Flight, button, link (same control again)"
      ],
      rejected: [
        "TAB → Book a Flight, button, link (tabIndex=-1 on the inner button did not help)"
      ],
      after: [
        "TAB → Book a Flight, link",
        "TAB → Explore Flights, link",
        "TAB → Book Your Flight Now, link"
      ]
    }
  },
  {
    id: "F-08",
    status: "verified — discovered by Bob’s /sweep, accepted by a human",
    wcag: "2.4.4 Link Purpose (In Context) (A); 1.1.1 Non-text Content (A)",
    component: "Footer GitHub icon link (axe-core flags this one too: link-name)",
    script: "TAB ×17 from top of /",
    expected: "“GitHub, link”",
    audio: {
      before: "../evidence/F-08/before_bob_listen.wav",
      after:  "../evidence/F-08/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB → content info landmark, github.com, link (the raw address)"
      ],
      after: [
        "TAB → content info landmark, GitHub, link"
      ]
    }
  },
  {
    id: "N-01",
    status: "fixed \u2014 confirmed by ear + human",
    wcag: "2.2.2 Pause, Stop, Hide (A)",
    component: "Animated starfield background, every page",
    audio: {
      ear: "../evidence/N-01/ear_check_bob_listen.wav"
    },
    transcript: {
      ear: [
        "Pause animation, button"
      ]
    },
    humanCheck: "Starfield freezes on click and resumes; button label toggles to \u201cResume animation\u201d. Verified visually 2026-09-25."
  },
  {
    id: "N-02",
    status: "verified",
    wcag: "4.1.3 Status Messages (AA)",
    component: "/flights results count while typing in the search field",
    script: "TAB ×7, then type “Mars”",
    expected: "The new count is announced politely, without interrupting typing",
    audio: {
      before: "../evidence/N-02/before_typing_listen.wav",
      after:  "../evidence/N-02/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TYPE → M, a, r, s … then silence (the count changed on screen only)"
      ],
      after: [
        "M → Showing 5 flights",
        "a → Showing 4 flights",
        "r, s → letters echoed; typing never interrupted"
      ]
    }
  }
  ,{
    id: "F-09",
    status: "verified",
    wcag: "2.1.1 Keyboard (A); 3.2.2 On Input (A)",
    component: "Sign In dialog: a regression Bob's own F-01 fix introduced (focus stolen on every keystroke)",
    script: "ENTER → TAB → TAB, type “Nobody”, TAB",
    expected: "The Name field keeps focus while typing; the next Tab says “Email, edit, required”",
    audio: {
      before: "../evidence/F-09/before_probe_typing_listen.wav",
      after:  "../evidence/F-09/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TYPE → N … then “Sign In, dialog” again: focus jumped out of the Name field",
        "TAB → Close modal, button (only “N” was typed)"
      ],
      after: [
        "TYPE → N, o, b, o, d, y",
        "TAB → Email, edit, required"
      ]
    }
  }
  ,{
    id: "F-10",
    status: "verified — discovered by Bob’s /earshot run, accepted by a human",
    wcag: "2.4.4 Link Purpose (A); 2.4.6 Headings and Labels (AA)",
    component: "/destinations/mars: two flight links both named “Book” (found by the one-command /earshot run)",
    script: "TAB ×9 from top of /destinations/mars",
    expected: "“Book Earth to Mars, Jan 01, 2099, link”, then “Book Moon to Mars, Jan 07, 2099, link”",
    audio: {
      before:   "../evidence/F-10/before_bob_earshot_sweep_listen.wav",
      rejected: "../evidence/F-10/after_bob_listen_v1.wav",
      after:    "../evidence/F-10/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB → Book, link",
        "TAB → Book, link (which flight?)"
      ],
      rejected: [
        "Bob’s first label: “Book flight Jan 01, 2099 1, link” (a bare flight id); a human rewrote the expectation"
      ],
      after: [
        "TAB → Book Earth to Mars, Jan 01, 2099, link",
        "TAB → Book Moon to Mars, Jan 07, 2099, link"
      ]
    }
  }
  ,{
    id: "F-11",
    status: "verified — discovered by Bob’s /earshot run, accepted by a human",
    wcag: "4.1.2 Name, Role, Value (A); 1.3.1 Info and Relationships (A)",
    component: "TodoMVC (second app): todo checkboxes have no name",
    script: "type two todos, then TAB ×4",
    expected: "“Buy milk, check box, not checked”",
    audio: {
      before: "../evidence/F-11/before_bob_earshot_sweep_listen.wav",
      after:  "../evidence/F-11/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB → list, with 2 items, check box, not checked (which todo?)",
        "TAB → check box, not checked"
      ],
      after: [
        "TAB → list, with 2 items, Buy milk, check box, not checked",
        "TAB → Walk dog, check box, not checked"
      ]
    }
  }
  ,{
    id: "F-12",
    status: "verified",
    wcag: "2.1.1 Keyboard (A); 4.1.2 Name, Role, Value (A)",
    component: "TodoMVC (second app): Delete buttons hidden until mouse hover, so keyboard users cannot delete (heard by a human in the sweep transcript)",
    script: "type “Buy milk”, then TAB ×3",
    expected: "“Delete Buy milk, button” after the checkbox",
    audio: {
      before: "../evidence/F-12/before_probe_listen.wav",
      after:  "../evidence/F-12/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB → check box, not checked",
        "TAB → All, link (no Delete button is ever reached)"
      ],
      after: [
        "TAB → Buy milk, check box, not checked",
        "TAB → Delete Buy milk, button"
      ]
    }
  },
  {
    id: "F-13",
    status: "verified",
    wcag: "4.1.2 Name, Role, Value (A)",
    component: "Uptime Kuma (third app, a real product): the logo is a silent Tab stop (discovered by Bob's /earshot run)",
    script: "from the top of the dashboard: TAB ×2",
    expected: "“Status Pages, link” on the second Tab",
    audio: {
      before: "../evidence/F-13/attempt1_rejected_aria_hidden_only_bob_listen.wav",
      after:  "../evidence/F-13/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB → banner landmark, Uptime Kuma, same page, link, current page",
        "TAB → (nothing: focus sits on the unnamed logo object; Bob's first fix, aria-hidden only, still sounded like this and was rejected)"
      ],
      after: [
        "TAB → banner landmark, Uptime Kuma, same page, link, current page",
        "TAB → list, with 3 items, Status Pages, link"
      ]
    }
  },
  {
    id: "F-14",
    status: "verified",
    wcag: "4.1.2 Name, Role, Value (A); 2.4.3 Focus Order (A)",
    component: "Uptime Kuma: the heartbeat chart is a second Tab stop inside every monitor link (discovered by Bob's /earshot run; guard test F-14b keeps the chart reachable where it is not in a link)",
    script: "from the top of the dashboard: TAB ×16",
    expected: "the Tab after “Galaxium … link” goes straight to “TodoMVC … link”",
    audio: {
      before: "../evidence/F-14/before_bob_earshot_sweep_listen.wav",
      after:  "../evidence/F-14/after_bob_listen.wav"
    },
    transcript: {
      before: [
        "TAB → 100%, Galaxium, Heartbeat history: 15 checks, 15 up, 0 down, link",
        "TAB → Heartbeat history: 15 checks, 15 up, 0 down, graphic, clickable, link",
        "TAB → 100%, TodoMVC, Heartbeat history: 15 checks, 15 up, 0 down, link"
      ],
      after: [
        "TAB → 100%, Galaxium, Heartbeat history: 30 checks, 30 up, 0 down, link",
        "TAB → 100%, TodoMVC, Heartbeat history: 30 checks, 30 up, 0 down, link"
      ]
    }
  }
];
