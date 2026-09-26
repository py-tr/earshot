/* global EARSHOT_DATA */
(function () {
  "use strict";

  var BADGE = {
    "verified":              ["VERIFIED",           "badge-verified"],
    "pending":               ["PENDING FIX",        "badge-pending"],
    "needs-human":           ["NEEDS HUMAN",        "badge-human"],
    "fixed \u2014 confirmed by ear + human": ["FIXED + HUMAN",  "badge-verified"],
    "verified \u2014 discovered by Bob\u2019s /sweep, accepted by a human": ["VERIFIED \u00b7 FOUND BY SWEEP", "badge-verified"]
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
        var blocks = [];
        if (finding.audio.before)   blocks.push(renderAudioBlock("Before",          finding.audio.before,   finding.transcript.before));
        if (finding.audio.rejected) blocks.push(renderAudioBlock("Rejected first fix", finding.audio.rejected, finding.transcript.rejected));
        if (finding.audio.after)    blocks.push(renderAudioBlock("After",           finding.audio.after,    finding.transcript.after));
        if (finding.audio.ear)      blocks.push(renderAudioBlock("By ear",          finding.audio.ear,      finding.transcript.ear));
        audioHtml = "<div class=\"audio-section\">" + blocks.join("") + "</div>";
      }
      var humanHtml = finding.humanCheck
        ? "<div class=\"reason-note\" role=\"note\"><strong>Human check:</strong> " + esc(finding.humanCheck) + "</div>"
        : "";
      var dlHtml =
        "<dl>" +
          "<dt>WCAG</dt><dd>" + esc(finding.wcag) + "</dd>" +
          "<dt>Component</dt><dd>" + esc(finding.component) + "</dd>" +
          (finding.script   ? "<dt>Script</dt><dd><code>" + esc(finding.script) + "</code></dd>" : "") +
          (finding.expected ? "<dt>Expected</dt><dd>" + esc(finding.expected) + "</dd>" : "") +
        "</dl>";
      bodyHtml = dlHtml + audioHtml + humanHtml;
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
    if (container.querySelector(".card")) return; // already baked into index.html (report/bake.py)
    container.innerHTML = EARSHOT_DATA.map(renderCard).join("");
  });
}());
