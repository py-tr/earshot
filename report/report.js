/* global EARSHOT_DATA */
(function () {
  "use strict";

  var BADGE = {
    "verified":   ["VERIFIED",      "badge-verified"],
    "pending":    ["PENDING FIX",   "badge-pending"],
    "needs-human":["NEEDS HUMAN",   "badge-human"]
  };

  function esc(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderAudioBlock(label, src, lines) {
    var transcriptHtml = lines.map(function (l) {
      return "<p>" + esc(l) + "</p>";
    }).join("");
    return (
      "<div class=\"audio-block\">" +
        "<h3>" + esc(label) + "</h3>" +
        "<audio controls aria-label=\"" + esc(label) + " recording\">" +
          "<source src=\"" + esc(src) + "\" type=\"audio/wav\">" +
          "Your browser does not support the audio element." +
        "</audio>" +
        "<div class=\"transcript\" aria-label=\"" + esc(label) + " transcript\">" +
          transcriptHtml +
        "</div>" +
      "</div>"
    );
  }

  function renderCard(finding) {
    var badge = BADGE[finding.status] || ["UNKNOWN", "badge-pending"];
    var bodyHtml = "";

    if (finding.status === "needs-human") {
      bodyHtml =
        "<dl>" +
          "<dt>WCAG</dt><dd>" + esc(finding.wcag) + "</dd>" +
          "<dt>Component</dt><dd>" + esc(finding.component) + "</dd>" +
        "</dl>" +
        "<div class=\"reason-note\" role=\"note\">" + esc(finding.reason) + "</div>";
    } else {
      var audioHtml = "";
      if (finding.audio && finding.transcript) {
        audioHtml =
          "<div class=\"audio-section\">" +
            renderAudioBlock("Before", finding.audio.before, finding.transcript.before) +
            renderAudioBlock("After",  finding.audio.after,  finding.transcript.after) +
          "</div>";
      }
      bodyHtml =
        "<dl>" +
          "<dt>WCAG</dt><dd>" + esc(finding.wcag) + "</dd>" +
          "<dt>Component</dt><dd>" + esc(finding.component) + "</dd>" +
          "<dt>Script</dt><dd><code>" + esc(finding.script) + "</code></dd>" +
          "<dt>Expected</dt><dd>" + esc(finding.expected) + "</dd>" +
        "</dl>" + audioHtml;
    }

    return (
      "<article class=\"card\" aria-labelledby=\"card-" + esc(finding.id) + "\">" +
        "<div class=\"card-header\">" +
          "<h2 id=\"card-" + esc(finding.id) + "\">" + esc(finding.id) + "</h2>" +
          "<span class=\"badge " + badge[1] + "\">" + badge[0] + "</span>" +
        "</div>" +
        bodyHtml +
      "</article>"
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    var container = document.getElementById("findings-list");
    if (!container || !window.EARSHOT_DATA) return;
    container.innerHTML = EARSHOT_DATA.map(renderCard).join("");
  });
}());
