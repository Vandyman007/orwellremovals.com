/* Wolves Removals — /storage-calculator/ engine
 * Choose how many storage pods you need (directly, or work it out from an optional
 * item inventory), then pick a start and end date. We count the days between them and
 * cost the storage at a tiered rate per pod per day (inc VAT): £2.50 (1–3 pods), £2.357 (4–5),
 * £2.214 (6–9), £2.071 (10+). No external libs. Served from 'self'.
 */
(function () {
  'use strict';
  var root = document.querySelector('[data-scalc]');
  if (!root) return;
  var slice = function (n) { return Array.prototype.slice.call(n); };

  /* ---- optional item inventory ---- */
  var tabs = slice(root.querySelectorAll('.scalc-tab'));
  var panels = slice(root.querySelectorAll('.scalc-panel'));
  var inputs = slice(root.querySelectorAll('input[data-cuft]'));
  var search = document.getElementById('scalc-search');

  /* ---- pods ---- */
  var podsNum = document.getElementById('scalc-pods-num');
  var podsDec = root.querySelector('[data-pods-dec]');
  var podsInc = root.querySelector('[data-pods-inc]');
  var podsFromItems = document.getElementById('scalc-pods-from-items');
  var podsRate = document.getElementById('scalc-pods-rate');

  /* ---- dates ---- */
  var fromDate = document.getElementById('scalc-from-date');
  var toDate = document.getElementById('scalc-to-date');
  var datesNote = document.getElementById('scalc-dates-note');
  var datesWrap = document.getElementById('scalc-dates-wrap');   // hidden when "I'm not sure yet"
  var durBtns = slice(root.querySelectorAll('.scalc-dur'));   // rough-length buttons + "not sure" (ongoing)
  var costLead = document.getElementById('scalc-cost-lead');

  /* ---- cover ---- */
  var coverInp = document.getElementById('scalc-cover');

  /* ---- summary ---- */
  var tilePods = document.getElementById('scalc-tile-pods');
  var tileDays = document.getElementById('scalc-tile-days');
  var tileCuft = document.getElementById('scalc-tile-cuft');
  var elRec = document.getElementById('scalc-rec');
  var elPrice = document.getElementById('scalc-storage-price');
  var elDaily = document.getElementById('scalc-storage-daily');
  var sumFrom = document.getElementById('scalc-sum-from');
  var sumTo = document.getElementById('scalc-sum-to');
  var sumDays = document.getElementById('scalc-sum-days');
  var sumCover = document.getElementById('scalc-sum-cover');
  var volWrap = document.getElementById('scalc-vol-wrap');
  var sumVol = document.getElementById('scalc-sum-vol');
  var invWrap = document.getElementById('scalc-inv-wrap');
  var elInv = document.getElementById('scalc-inventory');
  var quoteBtn = document.getElementById('scalc-quote');
  var reset = document.getElementById('scalc-reset');
  var ptVals = slice(root.querySelectorAll('.scalc-pt-val'));   // prices-by-term table

  var CONTAINER_CUFT = 250;
  var ITEM_BUFFER = 1.2;           // +20% on the itemised cube — a packing/access allowance "in case of issues"
  function podDaily(p) {            // tiered £ per pod per day (inc VAT) — the more pods, the lower the rate
    if (p <= 3) return 2.50;       // 1–3 pods
    if (p <= 5) return 2.357;      // 4–5 pods
    if (p <= 9) return 2.214;      // 6–9 pods
    return 2.071;                  // 10+ pods
  }
  function fmtRate(r) { var s = r.toFixed(3); if (s.charAt(s.length - 1) === '0') s = s.slice(0, -1); return '£' + s; }
  var pods = 1, cuftNow = 0, cumNow = 0, itemCount = 0;
  var ongoing = false;   // "I'm not sure yet" — billed monthly, no fixed dates

  function toISO(dt) { var m = dt.getMonth() + 1, d = dt.getDate(); return dt.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (d < 10 ? '0' : '') + d; }
  var today = '';
  try { today = toISO(new Date()); } catch (e) {}
  if (fromDate && today) fromDate.min = today;
  if (toDate && today) toDate.min = today;

  /* ---------- helpers ---------- */
  function money0(n) { return '£' + Math.round(n).toLocaleString('en-GB'); }
  function dailyTxt() { return fmtRate(podDaily(pods)); }   // per-pod rate at the current tier
  function fmtDate(v) { if (!v) return ''; var p = v.split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : v; }
  function daysBetween(a, b) {
    if (!a || !b) return 0;
    var da = new Date(a + 'T00:00:00'), db = new Date(b + 'T00:00:00');
    if (isNaN(da.getTime()) || isNaN(db.getTime())) return 0;
    return Math.round((db.getTime() - da.getTime()) / 86400000);
  }
  function approxSuffix(days) {  // a friendly "(~1 month)" hint; nothing for short stays
    if (days < 14) return '';
    if (days >= 30) { var mm = Math.round(days / 30.44 * 10) / 10; return ' (~' + mm + ' month' + (mm === 1 ? '' : 's') + ')'; }
    var w = Math.round(days / 7); return ' (~' + w + ' week' + (w !== 1 ? 's' : '') + ')';
  }
  function periodLabel(days) { return days + ' day' + (days !== 1 ? 's' : '') + approxSuffix(days); }

  /* ---------- room tabs + search ---------- */
  function activeTab() { for (var i = 0; i < tabs.length; i++) if (tabs[i].classList.contains('is-active')) return tabs[i]; return tabs[0]; }
  function showTab(id) {
    tabs.forEach(function (t) { var on = t.dataset.target === id; t.classList.toggle('is-active', on); t.setAttribute('aria-selected', on ? 'true' : 'false'); });
    panels.forEach(function (p) { p.hidden = (p.id !== id); });
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { if (search) search.value = ''; clearFilter(); showTab(t.dataset.target); }); });
  function clearFilter() { panels.forEach(function (p) { slice(p.querySelectorAll('.scalc-item')).forEach(function (it) { it.style.display = ''; }); }); }
  function filter() {
    var q = (search.value || '').trim().toLowerCase();
    if (!q) { clearFilter(); showTab(activeTab().dataset.target); return; }
    tabs.forEach(function (t) { t.classList.remove('is-active'); t.setAttribute('aria-selected', 'false'); });
    panels.forEach(function (p) {
      var any = false;
      slice(p.querySelectorAll('.scalc-item')).forEach(function (it) { var m = it.dataset.name.indexOf(q) >= 0; it.style.display = m ? '' : 'none'; if (m) any = true; });
      p.hidden = !any;
    });
  }
  if (search) search.addEventListener('input', filter);

  /* ---------- pods controls ---------- */
  function setPods(n) { pods = Math.max(1, n); if (podsNum) podsNum.textContent = pods; render(); }
  if (podsDec) podsDec.addEventListener('click', function () { setPods(pods - 1); });
  if (podsInc) podsInc.addEventListener('click', function () { setPods(pods + 1); });

  /* ---------- inventory -> volume -> suggested pods ---------- */
  function recalcItems() {
    var cuft = 0, count = 0, rooms = {};
    inputs.forEach(function (inp) {
      var q = parseInt(inp.value, 10) || 0;
      if (q < 0) { q = 0; inp.value = 0; }
      var st = inp.closest('.scalc-stepper'); if (st) st.classList.toggle('has-qty', q > 0);
      if (q > 0) {
        var pp = parseInt(inp.dataset.perpod, 10) || 0;
        // non-stackable items take a fixed pod footprint (250/perpod, no buffer); everything else is its cube + 20%
        cuft += pp > 0 ? q * (CONTAINER_CUFT / pp) : q * parseFloat(inp.dataset.cuft) * ITEM_BUFFER;
        count += q;
        var rm = inp.dataset.room || 'Items';
        (rooms[rm] = rooms[rm] || []).push(q + ' &times; ' + inp.dataset.label);
      }
    });
    var cum = cuft * 0.0283;                    // cu m derived from the effective cube
    cuftNow = cuft; cumNow = cum; itemCount = count;

    if (elInv) {
      if (count > 0) {
        var h = '';
        Object.keys(rooms).forEach(function (rm) {
          h += '<div class="scalc-inv-room">' + rm + '</div>';
          rooms[rm].forEach(function (li) { h += '<div class="scalc-inv-item">' + li + '</div>'; });
        });
        elInv.innerHTML = h;
      } else { elInv.innerHTML = '<p class="scalc-inv-empty">No items added yet.</p>'; }
    }

    if (count > 0) {
      var suggested = Math.max(1, Math.ceil(cuft / CONTAINER_CUFT));
      pods = suggested;
      if (podsNum) podsNum.textContent = pods;
      if (podsFromItems) podsFromItems.innerHTML = '&asymp; <strong>' + suggested + ' pod' + (suggested > 1 ? 's' : '') +
        '</strong> &mdash; ~' + Math.round(cuft) + ' cu ft including a 20% packing allowance. Adjust the number above if you like.';
    } else if (podsFromItems) { podsFromItems.textContent = ''; }
    render();
  }

  /* item steppers (delegated) */
  root.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.scalc-item [data-action]') : null;
    if (!b) return;
    var wrap = b.closest('.scalc-stepper'); if (!wrap) return;
    var inp = wrap.querySelector('input'); var v = parseInt(inp.value, 10) || 0;
    v += (b.dataset.action === 'inc') ? 1 : -1; if (v < 0) v = 0; inp.value = v;
    recalcItems();
  });
  inputs.forEach(function (i) { i.addEventListener('input', recalcItems); });

  /* ---------- render summary ---------- */
  function render() {
    var fv = fromDate ? fromDate.value : '', tv = toDate ? toDate.value : '';
    var days = 0, valid = false, dateErr = false, exact = false;
    if (ongoing) { valid = true; }                   // "not sure yet" — billed monthly, no dates
    else if (fv && tv) {                             // dates drive the cost (a rough length auto-fills them)
      var diff = daysBetween(fv, tv);
      if (diff >= 0) { exact = true; valid = true; days = diff + 1; }   // inclusive — 1st to 31st = 31
      else { dateErr = true; }
    }
    if (datesWrap) datesWrap.hidden = ongoing;        // dates disappear when ongoing
    var rate = podDaily(pods);
    var total = (valid && days > 0) ? pods * days * rate : 0;
    var monthly = pods * rate * 30.44;

    if (tilePods) tilePods.textContent = pods;
    if (tileDays) tileDays.textContent = ongoing ? '—' : (valid ? days : 0);
    if (tileCuft) tileCuft.textContent = Math.round(cuftNow);

    if (elRec) elRec.innerHTML = '<strong>' + pods + ' storage pod' + (pods > 1 ? 's' : '') + '</strong>' +
      '<span class="scalc-rec-sub">each holds ~250 cu ft / 7 cu m' + (itemCount > 0 ? (' &middot; ~' + Math.round(cuftNow) + ' cu ft to store (incl. 20%)') : '') + '</span>';

    if (ongoing) {
      if (elPrice) elPrice.textContent = money0(monthly);
      if (costLead) costLead.textContent = 'per month, ongoing';
    } else {
      if (elPrice) elPrice.textContent = (valid && days > 0) ? money0(total) : '—';
      if (costLead) costLead.textContent = 'for the period';
    }
    if (elDaily) elDaily.textContent = dailyTxt();
    if (podsRate) podsRate.innerHTML = '<strong>' + fmtRate(rate) + '</strong> per pod, per day';

    // prices-by-term table (always shown — updates with the pod count + tier)
    ptVals.forEach(function (el) {
      var dys = parseFloat(el.getAttribute('data-pt-days')) || 0;
      el.textContent = money0(pods * rate * dys) + (el.getAttribute('data-pt-unit') || '');
    });

    if (datesNote) {
      if (dateErr) datesNote.innerHTML = '<span class="scalc-dates-err">Please choose an end date on or after the start date.</span>';
      else if (tv && !fv) datesNote.innerHTML = '<span class="scalc-dates-err">Add your storage start date for an exact length.</span>';
      else if (ongoing) datesNote.innerHTML = '<strong>Ongoing storage</strong> &mdash; flexible and billed monthly, with no tie-in. Cancel any time.';
      else if (valid && days > 0) datesNote.innerHTML = '<strong>' + days + ' day' + (days !== 1 ? 's' : '') + '</strong> of storage' + approxSuffix(days);
      else datesNote.textContent = 'Pick a rough length above, or enter your own dates.';
    }

    if (sumFrom) sumFrom.textContent = fv ? fmtDate(fv) : '—';
    if (sumTo) sumTo.textContent = exact ? fmtDate(tv) : '—';
    if (sumDays) sumDays.textContent = ongoing ? 'Ongoing (billed monthly)' : (valid && days > 0 ? periodLabel(days) : '—');
    if (sumCover) sumCover.textContent = (coverInp && coverInp.checked) ? 'Standard + extended' : 'Standard';

    if (volWrap) volWrap.hidden = itemCount === 0;
    if (sumVol) sumVol.textContent = Math.round(cuftNow) + ' cu ft / ' + cumNow.toFixed(1) + ' cu m · ' + itemCount + ' items';
    if (invWrap) invWrap.hidden = itemCount === 0;

    if (quoteBtn) {
      var sb = [pods + ' storage pod' + (pods > 1 ? 's' : '')];
      if (ongoing) sb.push('Length: ongoing, billed monthly (from ' + money0(monthly) + '/month inc VAT)' + (fv ? ', from ' + fmtDate(fv) : ''));
      else if (valid && days > 0) {
        if (exact) sb.push('Period: ' + fmtDate(fv) + ' to ' + fmtDate(tv) + ' (' + periodLabel(days) + ')');
        else sb.push('Length: ' + periodLabel(days) + (fv ? ', from ' + fmtDate(fv) : ''));
        sb.push('Estimated cost: ' + money0(total) + ' inc VAT (' + dailyTxt() + '/pod/day)');
      }
      if (itemCount > 0) sb.push('From your items: ~' + Math.round(cuftNow) + ' cu ft / ' + cumNow.toFixed(1) + ' cu m, ' + itemCount + ' items');
      sb.push('Contents cover: ' + ((coverInp && coverInp.checked) ? 'standard + extended' : 'standard'));
      quoteBtn.href = '/get-a-quote/?service=Storage&details=' + encodeURIComponent(sb.join('; '));
    }
  }

  /* ---------- rough-length buttons: auto-fill the dates from today, or go ongoing ---------- */
  durBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var on = btn.classList.contains('is-sel');
      durBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
      ongoing = false;
      if (on) {                                              // un-picking clears the dates
        if (fromDate) fromDate.value = ''; if (toDate) toDate.value = '';
      } else {
        btn.classList.add('is-sel'); btn.setAttribute('aria-pressed', 'true');
        if (btn.hasAttribute('data-ongoing')) {              // "not sure yet" — hide + clear dates
          ongoing = true;
          if (fromDate) fromDate.value = ''; if (toDate) toDate.value = '';
        } else {                                             // fill start = today, end = today + (n-1) -> n inclusive days
          var n = parseInt(btn.dataset.days, 10) || 0;
          var s = new Date(), e = new Date(); e.setDate(e.getDate() + (n - 1));
          if (fromDate) fromDate.value = toISO(s);
          if (toDate) { toDate.value = toISO(e); toDate.min = toISO(s); }
        }
      }
      render();
    });
  });

  /* ---------- dates + cover (editing a date drops the rough-length pick) ---------- */
  function onDateEdit() {
    durBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
    ongoing = false;
    if (fromDate && fromDate.value && toDate) toDate.min = fromDate.value;
    render();
  }
  if (fromDate) fromDate.addEventListener('change', onDateEdit);
  if (toDate) toDate.addEventListener('change', onDateEdit);
  if (coverInp) coverInp.addEventListener('change', render);

  /* ---------- reset ---------- */
  if (reset) reset.addEventListener('click', function () {
    inputs.forEach(function (i) { i.value = 0; var st = i.closest('.scalc-stepper'); if (st) st.classList.remove('has-qty'); });
    if (search) { search.value = ''; clearFilter(); if (tabs.length) showTab(tabs[0].dataset.target); }
    if (podsFromItems) podsFromItems.textContent = '';
    pods = 1; if (podsNum) podsNum.textContent = 1;
    cuftNow = 0; cumNow = 0; itemCount = 0;
    if (fromDate) fromDate.value = '';
    if (toDate) { toDate.value = ''; if (today) toDate.min = today; }
    durBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
    ongoing = false;
    if (coverInp) coverInp.checked = false;
    if (elInv) elInv.innerHTML = '';
    render();
  });

  if (tabs.length) showTab(tabs[0].dataset.target);
  recalcItems();
})();

/* Desktop: the summary card is taller than the screen, so let it FOLLOW the scroll —
   its top stays in view as you scroll up, and its bottom (the CTA) comes into view as you
   scroll down. Mobile is untouched. */
(function () {
  var card = document.querySelector('[data-scalc] .scalc-results-card');
  var grid = document.querySelector('[data-scalc] .scalc');
  if (!card || !grid) return;
  var TOP = 160, GAP = 16;
  function scy() { return window.pageYOffset || document.documentElement.scrollTop || 0; }
  var lastY = scy(), pin = TOP, ticking = false;
  function apply() {
    ticking = false;
    if (window.innerWidth < 1024) { card.style.top = ''; return; }
    var wh = window.innerHeight, ch = card.offsetHeight, y = scy();
    if (ch <= wh - TOP - GAP) { card.style.top = TOP + 'px'; pin = TOP; lastY = y; return; }   // fits — plain top-sticky
    if (grid.getBoundingClientRect().top >= TOP) { pin = TOP; card.style.top = TOP + 'px'; lastY = y; return; }   // before the calc — show the top
    var dy = y - lastY; lastY = y;
    pin = dy > 0 ? Math.max(wh - ch - GAP, pin - dy)   // scrolling down — drift up to reveal the bottom
                 : Math.min(TOP, pin - dy);            // scrolling up — drift down to reveal the top
    card.style.top = pin + 'px';
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(apply); } }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', apply);
  apply();
})();
