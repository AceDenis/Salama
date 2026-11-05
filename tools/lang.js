/* ===== English / Kiswahili switch =====
   Every visible text on the page is looked up in window.SW_DICT (English -> Kiswahili) and replaced in place.
   It also covers text the app draws later, because it watches the page for changes. English is always the source of truth.
   Text that is not in the dictionary stays in English. Kiswahili is a DRAFT until a translator has checked it. */
(function () {
  "use strict";
  var KEY = "salama_lang", D = window.SW_DICT || {}, RX = window.SW_RX || [], ATTRS = ["placeholder", "title", "aria-label", "alt"];
  var lang = "en"; try { var s = JSON.parse(localStorage.getItem(KEY)); if (s === "sw" || s === "en") lang = s; } catch (e) { }
  var missing = {}, norm = function (s) { return s.replace(/\s+/g, " ").trim(); };
  function tr(raw) {
    var n = norm(raw); if (!n) return null; var r = D[n]; if (r !== undefined) return r;
    for (var i = 0; i < RX.length; i++) { var m = n.match(RX[i][0]); if (m) return RX[i][1].apply(null, m); }
    return null;
  }
  function skip(el) { return !el || /^(SCRIPT|STYLE|TEXTAREA|NOSCRIPT)$/.test(el.nodeName) || (el.closest && el.closest("[data-notr]")); }
  function text(node) {
    if (node.__tr !== undefined) {
      if (node.data === node.__tr) { if (lang === "en") { node.data = node.__en; node.__tr = undefined; } return; }
      node.__tr = undefined;                                   // the page changed this text itself: treat as new
    }
    if (lang !== "sw" || skip(node.parentNode)) return;
    var raw = node.data, r = tr(raw);
    if (r === null) { var n = norm(raw); if (/[A-Za-z]{3}/.test(n)) missing[n] = 1; return; }
    node.__en = raw; node.data = raw.match(/^\s*/)[0] + r + raw.match(/\s*$/)[0]; node.__tr = node.data;
  }
  function attrs(el) {
    if (!el.getAttribute || skip(el)) return;
    var list = ATTRS.slice(); if (el.nodeName === "INPUT" && /^(button|submit)$/.test(el.type)) list.push("value");
    el.__ea = el.__ea || {};
    list.forEach(function (a) {
      var v = el.getAttribute(a); if (v === null) return; var e = el.__ea[a];
      if (e && v === e.t) { if (lang === "en") { el.setAttribute(a, e.o); delete el.__ea[a]; } return; }
      if (e) delete el.__ea[a];
      if (lang !== "sw") return; var r = tr(v);
      if (r === null) { if (/[A-Za-z]{3}/.test(v)) missing[norm(v)] = 1; return; }
      el.__ea[a] = { o: v, t: r }; el.setAttribute(a, r);
    });
  }
  function walk(root) {
    if (!root) return;
    if (root.nodeType === 3) return text(root);
    if (root.nodeType !== 1) return;
    attrs(root);
    var w = document.createTreeWalker(root, 5, null), n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) text(n); else attrs(n); }
  }
  function title() {
    if (document.__t0 === undefined) document.__t0 = document.title;
    document.title = lang === "sw" ? (tr(document.__t0) || document.__t0) : document.__t0;
  }
  function apply() { document.documentElement.lang = lang === "sw" ? "sw" : "en"; title(); walk(document.body); paint(); }
  function paint() {
    var b = document.querySelectorAll(".langsw button"); for (var i = 0; i < b.length; i++) { b[i].setAttribute("aria-pressed", String(b[i].dataset.l === lang)); b[i].classList.toggle("on", b[i].dataset.l === lang); }
  }
  var mo = new MutationObserver(function (ms) {
    ms.forEach(function (m) {
      if (m.type === "childList") m.addedNodes.forEach(function (n) { walk(n); });
      else if (m.type === "characterData") text(m.target);
      else if (m.type === "attributes") attrs(m.target);
    });
  });
  function set(l, quiet) {
    if (l !== "en" && l !== "sw") return; lang = l; if (!quiet) { try { localStorage.setItem(KEY, JSON.stringify(l)); } catch (e) { } }
    apply(); try { window.dispatchEvent(new CustomEvent("salama-lang", { detail: l })); } catch (e) { }
  }
  /* the switch: two small buttons. Place it with <span class="langsw" data-notr></span> or call Lang.mount(element). */
  function mount(el) {
    el.className = (el.className ? el.className + " " : "") + "langsw"; el.setAttribute("data-notr", "");
    el.innerHTML = '<button type="button" data-l="en" aria-label="English">EN</button><button type="button" data-l="sw" aria-label="Kiswahili">SW</button>';
    el.addEventListener("click", function (e) { var b = e.target.closest("button"); if (b) set(b.dataset.l); });
    paint();
  }
  window.addEventListener("storage", function (e) { if (e.key === KEY) { try { var v = JSON.parse(e.newValue); if (v !== lang) set(v, true); } catch (x) { } } });
  window.Lang = { get: function () { return lang; }, set: set, mount: mount, apply: apply, tr: function (s) { return lang === "sw" ? (tr(s) || s) : s; }, missing: function () { return Object.keys(missing); }, size: Object.keys(D).length };
  function start() {
    var st = document.createElement("style");
    st.textContent = ".langsw{display:inline-flex;gap:0;border:1px solid currentColor;border-radius:8px;overflow:hidden;vertical-align:middle}.langsw button{font:600 .75rem/1 system-ui,sans-serif;padding:6px 9px;border:0;background:transparent;color:inherit;cursor:pointer;opacity:.7}.langsw button.on{background:#fff;color:#12302E;opacity:1}";
    document.head.appendChild(st);
    document.querySelectorAll("[data-langsw]").forEach(mount);
    apply(); mo.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
