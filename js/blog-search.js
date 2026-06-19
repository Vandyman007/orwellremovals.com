/* Smart typeahead for the blog index: ranked article matches (with thumbnails) +
   topic suggestions as you type, synonym-aware, keyboard-navigable. Also live-filters
   the article grid. Progressive enhancement — the page works fine without JS. */
(function () {
  var input = document.getElementById('blog-search');
  var box = document.getElementById('blog-search-results');
  var idxEl = document.getElementById('blog-search-index');
  if (!input || !box || !idxEl) return;

  var DATA = { posts: [], topics: [] };
  try { DATA = JSON.parse(idxEl.textContent); } catch (e) { return; }
  var POSTS = DATA.posts || [], TOPICS = DATA.topics || [];
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-blog-card]'));
  var empty = document.getElementById('blog-search-empty');
  var active = -1;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function reEsc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function tokenize(q) { return q.trim().toLowerCase().split(/\s+/).filter(Boolean); }

  // Relevance score — title hits beat category hits beat body hits; all tokens must match.
  function scorePost(p, tokens) {
    var s = p.s || '', title = (p.t || '').toLowerCase(), cat = (p.c || '').toLowerCase(), score = 0;
    for (var i = 0; i < tokens.length; i++) {
      var tk = tokens[i];
      if (s.indexOf(tk) === -1) return 0;               // AND match across the blob
      if (title.indexOf(tk) === 0) score += 12;          // title starts with token
      else if (new RegExp('\\b' + reEsc(tk)).test(title)) score += 9; // word-start in title
      else if (title.indexOf(tk) > -1) score += 6;       // anywhere in title
      if (cat.indexOf(tk) > -1) score += 5;              // category hit
      score += 1;                                        // base (matched in blob/synonyms)
    }
    if (tokens.length > 1 && title.indexOf(tokens.join(' ')) > -1) score += 8; // exact phrase
    return score;
  }

  function search(q) {
    var tokens = tokenize(q);
    if (!tokens.length) return { topics: [], posts: [] };
    var scored = [];
    for (var i = 0; i < POSTS.length; i++) {
      var sc = scorePost(POSTS[i], tokens);
      if (sc > 0) scored.push({ p: POSTS[i], sc: sc });
    }
    scored.sort(function (a, b) { return b.sc - a.sc; });
    var ql = q.trim().toLowerCase(), tops = [];
    for (var j = 0; j < TOPICS.length; j++) {
      var ln = TOPICS[j].toLowerCase();
      var hit = ln.indexOf(ql) === 0 || tokens.some(function (t) { return t.length >= 3 && ln.indexOf(t) > -1; });
      if (hit) tops.push(TOPICS[j]);
    }
    return { topics: tops.slice(0, 3), posts: scored.slice(0, 6).map(function (x) { return x.p; }) };
  }

  function filterGrid(q) {
    var tokens = tokenize(q), n = 0;
    cards.forEach(function (c) {
      var dq = c.getAttribute('data-q') || '';
      var m = !tokens.length || tokens.every(function (t) { return dq.indexOf(t) > -1; });
      c.style.display = m ? '' : 'none';
      if (m) n++;
    });
    if (empty) empty.style.display = (tokens.length && !n) ? '' : 'none';
  }

  function render(q) {
    if (!q.trim()) { close(); return; }
    var r = search(q), html = '';
    if (r.topics.length) {
      html += '<div class="px-4 pt-3 pb-1 text-xs font-bold uppercase tracking-wide text-darkgrey">Topics</div>';
      r.topics.forEach(function (t) {
        html += '<button type="button" role="option" data-topic="' + esc(t) + '" '
          + 'class="bsr-item w-full text-left flex items-center gap-2 px-4 py-2 hover:bg-lightgrey">'
          + '<svg class="w-4 h-4 text-orange shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
          + '<path d="M10 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V8a2 2 0 00-2-2h-8l-2-2z"/></svg>'
          + '<span class="font-semibold text-black">' + esc(t) + '</span>'
          + '<span class="ml-auto text-xs text-darkgrey">Browse</span></button>';
      });
    }
    if (r.posts.length) {
      html += '<div class="px-4 pt-3 pb-1 text-xs font-bold uppercase tracking-wide text-darkgrey">Articles</div>';
      r.posts.forEach(function (p) {
        html += '<a href="' + esc(p.u) + '" role="option" class="bsr-item flex items-center gap-3 px-4 py-2 hover:bg-lightgrey">'
          + '<img src="' + esc(p.i) + '" alt="" width="48" height="48" loading="lazy" class="w-12 h-12 rounded object-cover shrink-0">'
          + '<span class="min-w-0"><span class="block font-semibold text-black leading-snug line-clamp-2">' + esc(p.t) + '</span>'
          + '<span class="block text-xs text-orange uppercase font-semibold">' + esc(p.c) + '</span></span></a>';
      });
    }
    if (!html) html = '<div class="px-4 py-4 text-darkgrey">No results for &ldquo;' + esc(q.trim()) + '&rdquo;.</div>';
    box.innerHTML = html;
    box.classList.remove('hidden');
    input.setAttribute('aria-expanded', 'true');
    active = -1;
  }

  function close() {
    box.classList.add('hidden');
    box.innerHTML = '';
    input.setAttribute('aria-expanded', 'false');
    active = -1;
  }

  function setActive(i) {
    var els = box.querySelectorAll('.bsr-item');
    if (active > -1 && els[active]) els[active].classList.remove('bg-lightgrey');
    active = i;
    if (active > -1 && els[active]) {
      els[active].classList.add('bg-lightgrey');
      els[active].scrollIntoView({ block: 'nearest' });
    }
  }

  function applyTopic(t) {
    input.value = t;
    render(t);
    filterGrid(t);
    input.focus();
  }

  input.addEventListener('input', function () { render(input.value); filterGrid(input.value); });
  input.addEventListener('focus', function () { if (input.value.trim()) render(input.value); });

  input.addEventListener('keydown', function (e) {
    var els = box.querySelectorAll('.bsr-item');
    if (e.key === 'ArrowDown') { e.preventDefault(); if (els.length) setActive(Math.min(active + 1, els.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); if (els.length) setActive(Math.max(active - 1, 0)); }
    else if (e.key === 'Enter') {
      if (active > -1 && els[active]) { e.preventDefault(); els[active].click(); }
    } else if (e.key === 'Escape') { close(); }
  });

  box.addEventListener('click', function (e) {
    var t = e.target.closest('[data-topic]');
    if (t) { e.preventDefault(); applyTopic(t.getAttribute('data-topic')); }
  });

  document.addEventListener('click', function (e) {
    if (!box.contains(e.target) && e.target !== input) close();
  });
})();
