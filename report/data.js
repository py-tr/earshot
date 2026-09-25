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
    status: "needs-human",
    wcag: "4.1.3 Status Messages (AA)",
    component: "/flights results count",
    reason: "Live-region politeness and non-interruption of typing requires manual screen-reader observation; earshot cannot assert ARIA live behaviour from audio alone."
  }
];
