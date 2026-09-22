/* ==========================================================================
   SOL — CUSTOM PIXEL EVENTS
   --------------------------------------------------------------------------
   The Meta base code (init + PageView) is inlined in the <head> of every
   page, which is what Meta's detection tools look for. This file only adds
   the extra events on top of it:

     ViewContent  — a job page was opened
     ExpandJD     — someone opened the full job description
     Lead         — someone clicked through to email us

   Pixel ID lives in the inline snippet in each page's <head>, not here.
   ========================================================================== */

(function () {
  "use strict";

  // The base code runs first and defines fbq. If it is missing — blocked by
  // an ad blocker, or the snippet was removed — do nothing rather than error.
  if (typeof window.fbq !== "function") return;

  var body = document.body || {};
  var get  = function (k) { return body.getAttribute ? body.getAttribute(k) : null; };
  var page = get("data-page");   // index | role | privacy | 404
  var role = get("data-role");   // e.g. "Sous Chef"
  var slug = get("data-slug");   // e.g. "sous-chef"

  // --- ViewContent --------------------------------------------------------
  // Fires on pages that represent a job. This is what the retargeting
  // audience is built from.
  if (page === "role" && role) {
    fbq("track", "ViewContent", {
      content_name: role,
      content_category: "Job posting",
      content_ids: [slug],
      content_type: "job"
    });
  } else if (page === "index") {
    fbq("track", "ViewContent", {
      content_name: "Careers index",
      content_category: "Job posting"
    });
  }

  // --- ExpandJD (custom) --------------------------------------------------
  // Someone opened the full job description. A far better retargeting
  // audience than "visited the page".
  document.addEventListener("toggle", function (e) {
    var el = e.target;
    if (el && el.tagName === "DETAILS" && el.open && el.classList.contains("full")) {
      fbq("trackCustom", "ExpandJD", { content_name: role || "unknown" });
    }
  }, true);

  // --- Lead ---------------------------------------------------------------
  // A click on any mailto link to the jobs inbox. Deliberately NOT fired on
  // the "Apply for this role" button, which only scrolls down the page.
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest
      ? e.target.closest('a[href^="mailto:jobs@sol.pizza"]')
      : null;
    if (!a) return;
    fbq("track", "Lead", {
      content_name: role || "Careers index",
      content_category: "Job application"
    });
  }, true);
})();
