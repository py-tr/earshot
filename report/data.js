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
    status: "pending",
    wcag: "2.4.3 Focus Order (A)",
    component: "Sign In dialog",
    script: "ENTER, TAB \u00d75, SHIFT+TAB, ESCAPE",
    expected: "Fifth Tab wraps to \u201cClose modal, button\u201d. After Escape: \u201cSelect Seat Class, button\u201d."
  },
  {
    id: "F-03",
    status: "pending",
    wcag: "1.3.1 Info and Relationships (A); 4.1.2 Name, Role, Value (A)",
    component: "Sign In form fields",
    script: "ENTER, TAB, TAB",
    expected: "\u201cName, edit\u201d, then \u201cEmail, edit\u201d"
  },
  {
    id: "N-01",
    status: "needs-human",
    wcag: "2.2.2 Pause, Stop, Hide (A)",
    component: "Animated starfield background, every page",
    reason: "No automated key sequence can verify that a Pause/Stop/Hide control exists and works; requires manual visual and AT inspection."
  },
  {
    id: "N-02",
    status: "needs-human",
    wcag: "4.1.3 Status Messages (AA)",
    component: "/flights results count",
    reason: "Live-region politeness and non-interruption of typing requires manual screen-reader observation; earshot cannot assert ARIA live behaviour from audio alone."
  }
];
