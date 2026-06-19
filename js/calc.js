/* Wolves Removals — Removals & Storage Calculator (modelled on Mark Ratcliffe).
 * Three modes (radios name="calc-mode"): removals | storage | both.
 *   • Removals leg : volume cost (MRM anchors) + miles × vehicle mile-rate.  VAT shown, added at booking.
 *   • Storage leg  : pods × tiered £/pod/day (£2.50→£2.071, more pods = lower) × days.
 *   • Grand total  : removals nett + storage (NETT — "+ VAT at booking").
 * Elements tagged data-show-modes="removals|storage|both" are shown/hidden by mode.
 */
(function () {
  'use strict';
  var root = document.querySelector('[data-calc]');
  if (!root) return;
  var slice = function (n) { return Array.prototype.slice.call(n); };

  var modeRadios = slice(root.querySelectorAll('input[name="calc-mode"]'));
  var showEls = slice(root.querySelectorAll('[data-show-modes]'));
  var tabs   = slice(root.querySelectorAll('.scalc-tab'));
  var panels = slice(root.querySelectorAll('.scalc-panel'));
  var inputs = slice(root.querySelectorAll('input[data-cuft]'));
  var propBtns = slice(root.querySelectorAll('.scalc-opt[data-prop]'));
  var search = document.getElementById('scalc-search');
  var fromInp = document.getElementById('scalc-from-pc');
  var toInp   = document.getElementById('scalc-to-pc');
  var milesInp = document.getElementById('scalc-miles');
  var daysInp = document.getElementById('scalc-days');
  var dateInp = document.getElementById('scalc-date');
  var cuftInput = document.getElementById('scalc-cuft-input');
  var cuftHint = document.getElementById('scalc-cuft-hint');
  var calcDistBtn = document.getElementById('scalc-calc-dist');
  var distStatus = document.getElementById('scalc-dist-status');
  var adjustManualBtn = document.getElementById('scalc-adjust-manual');
  var manualWrap = document.getElementById('scalc-manual-wrap');
  var invToggle = document.getElementById('scalc-inv-toggle');
  var invToggleLabel = document.getElementById('scalc-inv-toggle-label');
  var tickManualBtn = document.getElementById('scalc-tick-manual');
  var picker = document.getElementById('scalc-picker');
  var selectedPreset = '';
  var DEFAULT_HINT = cuftHint ? cuftHint.innerHTML : '';
  var qForm = document.getElementById('scalc-quote-form');
  var qMsg = document.getElementById('scalc-quote-msg');
  var LAST = {};
  var reset  = document.getElementById('scalc-reset');
  var quoteBtn = document.getElementById('scalc-quote');

  var elCuft = document.getElementById('scalc-cuft');
  var elCum  = document.getElementById('scalc-cum');
  var elCount = document.getElementById('scalc-count');
  var elLoad = document.getElementById('scalc-load');
  var elGrand = document.getElementById('scalc-grand');
  var elHeadline = document.getElementById('scalc-headline');
  var elInv  = document.getElementById('scalc-inventory');

  var cV = document.getElementById('scalc-c-vehicle'), cVol = document.getElementById('scalc-c-volume'),
      cMile = document.getElementById('scalc-c-mileage'), cNett = document.getElementById('scalc-c-nett'),
      cVat = document.getElementById('scalc-c-vat'), cTot = document.getElementById('scalc-c-total');
  var sPods = document.getElementById('scalc-s-pods'), sDaily = document.getElementById('scalc-s-daily'),
      sTot = document.getElementById('scalc-s-total'), sReq = document.getElementById('scalc-s-podsreq');
  var splitRem = document.getElementById('scalc-split-rem'), splitSto = document.getElementById('scalc-split-sto'),
      splitStoLab = document.getElementById('scalc-split-sto-label');

  var CONTAINER_CUFT = 250, CUFT_PER_SQFT = 7;
  var VAT_RATE = 0.20;
  function podDaily(p) { if (p <= 3) return 2.50; if (p <= 5) return 2.357; if (p <= 9) return 2.214; return 2.071; }
  function fmtRate(r) { var s = r.toFixed(3); if (s.charAt(s.length - 1) === '0') s = s.slice(0, -1); return '£' + s; }
  var PRICE_ANCHORS = [[300, 300], [500, 500], [800, 650], [1000, 900], [1800, 1500], [2800, 2500]];

  if (dateInp) { try { dateInp.min = new Date().toISOString().slice(0, 10); } catch (e) {} }

  function gbp(n)  { return '£' + (n || 0).toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function gbp0(n) { return '£' + Math.round(n || 0).toLocaleString('en-GB'); }
  function volumeCost(cuft) {
    if (cuft <= PRICE_ANCHORS[0][0]) return PRICE_ANCHORS[0][1];
    for (var i = 1; i < PRICE_ANCHORS.length; i++) {
      var a = PRICE_ANCHORS[i - 1], b = PRICE_ANCHORS[i];
      if (cuft <= b[0]) return a[1] + (cuft - a[0]) * (b[1] - a[1]) / (b[0] - a[0]);
    }
    var L = PRICE_ANCHORS[PRICE_ANCHORS.length - 1], P = PRICE_ANCHORS[PRICE_ANCHORS.length - 2];
    return L[1] + (cuft - L[0]) * (L[1] - P[1]) / (L[0] - P[0]);
  }
  function vehicleFor(cuft) {
    if (cuft <= 0) return null;
    if (cuft <= 800) return { name: 'Luton Van (3.5t)', mileRate: 2.00, crew: cuft <= 350 ? '2 movers' : '2–3 movers', loads: 1 };
    if (cuft <= 1500) return { name: '7.5 Tonne Lorry', mileRate: 2.75, crew: '3 movers', loads: 1 };
    if (cuft <= 2500) return { name: '18 Tonne Lorry', mileRate: 4.00, crew: '3–4 movers', loads: 1 };
    return { name: '18 Tonne Lorry (or two loads)', mileRate: 4.00, crew: '4 movers', loads: 2 };  // two loads = double the mileage
  }

  /* ---------- mode ---------- */
  function getMode() { for (var i = 0; i < modeRadios.length; i++) if (modeRadios[i].checked) return modeRadios[i].value; return 'both'; }
  function applyMode() {
    var mode = getMode();
    root.setAttribute('data-calc-mode', mode);
    showEls.forEach(function (el) { el.style.display = el.getAttribute('data-show-modes').indexOf(mode) > -1 ? '' : 'none'; });
    render();
  }

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

  function fmtDate(v) { if (!v) return ''; var p = v.split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : v; }

  /* ---------- render everything ---------- */
  function render() {
    var cuft = 0, cum = 0, count = 0, rooms = {};
    inputs.forEach(function (inp) {
      var q = parseInt(inp.value, 10) || 0; if (q < 0) { q = 0; inp.value = 0; }
      var st = inp.closest('.scalc-stepper'); if (st) st.classList.toggle('has-qty', q > 0);
      if (q > 0) {
        cuft += q * parseFloat(inp.dataset.cuft); cum += q * parseFloat(inp.dataset.cum); count += q;
        var rm = inp.dataset.room || 'Items'; (rooms[rm] = rooms[rm] || []).push(q + ' &times; ' + inp.dataset.label);
      }
    });
    // Volume = ticked items if any, otherwise the editable cubic-ft box.
    var manual = cuftInput ? (parseInt(cuftInput.value, 10) || 0) : 0;
    var eff = count > 0 ? cuft : manual;
    var effCum = count > 0 ? cum : Math.round(manual * 0.0283 * 100) / 100;
    if (count > 0 && cuftInput) cuftInput.value = Math.round(cuft);  // keep the box in sync with the inventory
    if (elCuft) elCuft.textContent = Math.round(eff);
    if (elCum) elCum.textContent = effCum.toFixed(2);
    if (elCount) elCount.textContent = count;

    var mode = getMode();
    var vc = vehicleFor(eff);
    if (elLoad) elLoad.textContent = vc ? vc.name : '—';

    /* --- removals leg --- */
    var miles = milesInp ? (parseInt(milesInp.value, 10) || 0) : 0;
    var volCost = eff > 0 ? volumeCost(eff) : 0;
    var loads = vc ? (vc.loads || 1) : 1;
    var mileCost = miles * (vc ? vc.mileRate : 0) * loads;
    var removalsNett = (mode === 'storage') ? 0 : (volCost + mileCost);
    var removalsVat = removalsNett * VAT_RATE;
    if (cV) cV.textContent = vc ? vc.name : '—';
    if (cVol) cVol.textContent = gbp(volCost) + (eff > 0 ? (' (' + Math.round(eff) + ' cu ft)') : '');
    if (cMile) cMile.textContent = gbp(mileCost) + (miles > 0 && vc ? (' (' + miles + ' × £' + vc.mileRate.toFixed(2) + (loads > 1 ? ' × ' + loads + ' loads' : '') + ')') : '');
    if (cNett) cNett.textContent = gbp(removalsNett);
    if (cVat) cVat.textContent = gbp(removalsVat);
    if (cTot) cTot.textContent = gbp(removalsNett);

    /* --- storage leg --- */
    var pods = eff > 0 ? Math.max(1, Math.ceil(eff / CONTAINER_CUFT)) : 0;
    var sqft = eff > 0 ? Math.ceil(eff / CUFT_PER_SQFT) : 0;
    var days = daysInp ? (parseInt(daysInp.value, 10) || 0) : 0;
    var wantsStorage = (mode === 'storage' || mode === 'both');
    var podRate = podDaily(pods);
    var dailyV = wantsStorage ? pods * podRate : 0;
    var storageTotal = wantsStorage ? dailyV * days : 0;
    if (sPods) sPods.textContent = pods > 0 ? (pods + ' pod' + (pods > 1 ? 's' : '')) : '—';
    if (sDaily) sDaily.textContent = pods > 0 ? (fmtRate(podRate) + '/pod/day') : '£0.00';
    if (sTot) sTot.textContent = gbp(storageTotal) + (days > 0 ? (' (' + days + ' days)') : '');
    if (sReq) sReq.textContent = pods > 0 ? (pods + ' pod' + (pods > 1 ? 's' : '') + ' · ~' + sqft + ' sq ft') : '—';

    /* --- grand total (NETT — VAT added at booking) --- */
    var grand = removalsNett + storageTotal;
    if (elGrand) elGrand.textContent = gbp0(grand);

    if (splitRem) splitRem.textContent = gbp(removalsNett);
    if (splitSto) splitSto.textContent = gbp(storageTotal);
    if (splitStoLab) splitStoLab.textContent = 'Storage (' + days + ' day' + (days === 1 ? '' : 's') + ')';

    if (elHeadline) {
      if (eff > 0) {
        var bits = [];
        if (mode !== 'storage' && vc) bits.push(vc.name);
        if (mode !== 'storage' && miles > 0) bits.push(miles + ' mi');
        if (mode !== 'removals' && pods > 0) bits.push(days + ' days storage');
        elHeadline.textContent = Math.round(eff) + ' cu ft · + VAT at booking' + (bits.length ? ' · ' + bits.join(' · ') : '');
      } else {
        elHeadline.textContent = 'Live estimate · updates as you type';
      }
    }

    var invList = '';
    if (elInv) {
      if (count > 0) {
        var h = '';
        Object.keys(rooms).forEach(function (rm) {
          h += '<div class="scalc-inv-room">' + rm + '</div>';
          rooms[rm].forEach(function (li) { h += '<div class="scalc-inv-item">' + li + '</div>'; });
          invList += rm + ': ' + rooms[rm].join(', ') + '; ';
        });
        elInv.innerHTML = h;
      } else {
        elInv.innerHTML = '<p class="scalc-inv-empty">No items selected yet — pick a home size above or add items.</p>';
      }
    }
    invList = invList.replace(/&times;/g, 'x').replace(/&amp;/g, '&');

    var fr = fromInp ? fromInp.value.trim() : '', to = toInp ? toInp.value.trim() : '';
    LAST = {
      service: mode === 'removals' ? 'Removals' : mode === 'storage' ? 'Storage' : 'Removals & Storage',
      mode: mode, cuft: Math.round(eff), cum: effCum.toFixed(2), items: count,
      vehicle: (mode !== 'storage' && vc) ? vc.name : '', crew: (mode !== 'storage' && vc) ? vc.crew : '', miles: miles,
      volumeCost: gbp(volCost), mileage: gbp(mileCost), removalsNett: gbp(removalsNett), removalsVat: gbp(removalsVat),
      pods: (mode !== 'removals') ? pods : 0, days: days, dailyRate: pods > 0 ? (fmtRate(podRate) + '/pod/day') : '', storageTotal: gbp(storageTotal),
      grand: gbp0(grand), route: (fr || to) ? ((fr || '?') + ' to ' + (to || '?')) : '', inventory: invList
    };
  }

  /* ---------- events ---------- */
  modeRadios.forEach(function (r) { r.addEventListener('change', applyMode); });
  root.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-action]') : null;
    if (!b) return;
    var wrap = b.closest('.scalc-stepper'); if (!wrap) return;
    var inp = wrap.querySelector('input'); var v = parseInt(inp.value, 10) || 0;
    v += (b.dataset.action === 'inc') ? 1 : -1; if (v < 0) v = 0; inp.value = v; render();
  });
  inputs.forEach(function (i) { i.addEventListener('input', render); });
  propBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var on = btn.classList.contains('is-sel');
      propBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
      inputs.forEach(function (i) { i.value = 0; });          // home size sets the cubic-ft figure; inventory is optional
      if (!on) {
        btn.classList.add('is-sel'); btn.setAttribute('aria-pressed', 'true');
        selectedPreset = btn.getAttribute('data-preset') || '';
        if (cuftInput) cuftInput.value = parseInt(btn.getAttribute('data-vol'), 10) || 0;
        if (cuftHint) cuftHint.innerHTML = 'Typical ' + btn.getAttribute('data-label') + ': ' +
          (btn.getAttribute('data-range') || '') + ' cu ft. Auto-fills with this figure — refine it with the inventory above, or edit it here.';
        if (invToggleLabel) invToggleLabel.textContent = 'Use our ' + btn.getAttribute('data-label') + ' inventory list?';
      } else {
        selectedPreset = '';
        if (cuftInput) cuftInput.value = 0;
        if (cuftHint) cuftHint.innerHTML = DEFAULT_HINT;
        if (invToggleLabel) invToggleLabel.textContent = 'Use our typical inventory list?';
      }
      render();
    });
  });
  if (cuftInput) cuftInput.addEventListener('input', function () {
    inputs.forEach(function (i) { i.value = 0; });            // typing a figure is a manual override — drop the inventory
    render();
  });
  /* ---- distance lookup (postcodes.io): straight-line × road factor × 2 for round trip ---- */
  function ukpc(s) { var m = (s || '').toUpperCase().replace(/\s+/g, ' ').match(/[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}/); return m ? m[0].replace(/\s+/g, '') : ''; }
  function setDist(t, ok) { if (distStatus) { distStatus.textContent = t; distStatus.className = 'scalc-dist-status' + (ok === false ? ' is-err' : ok === true ? ' is-ok' : ''); } }
  function haversine(la1, lo1, la2, lo2) {
    var R = 3958.8, toR = Math.PI / 180, dLa = (la2 - la1) * toR, dLo = (lo2 - lo1) * toR;
    var x = Math.sin(dLa / 2) * Math.sin(dLa / 2) + Math.cos(la1 * toR) * Math.cos(la2 * toR) * Math.sin(dLo / 2) * Math.sin(dLo / 2);
    return R * 2 * Math.asin(Math.sqrt(x));
  }
  if (calcDistBtn) calcDistBtn.addEventListener('click', function () {
    var a = ukpc(fromInp && fromInp.value), b = ukpc(toInp && toInp.value);
    if (!a || !b) { setDist('Enter both postcodes, or adjust manually.', false); return; }
    setDist('Calculating…');
    Promise.all([
      fetch('https://api.postcodes.io/postcodes/' + encodeURIComponent(a)).then(function (r) { return r.json(); }),
      fetch('https://api.postcodes.io/postcodes/' + encodeURIComponent(b)).then(function (r) { return r.json(); })
    ]).then(function (res) {
      var p = res[0] && res[0].result, q = res[1] && res[1].result;
      if (!p || !q) { setDist('Postcode not found — adjust manually.', false); return; }
      var round = Math.round(haversine(p.latitude, p.longitude, q.latitude, q.longitude) * 1.3 * 2);
      if (milesInp) milesInp.value = round;
      if (manualWrap) { manualWrap.hidden = false; if (adjustManualBtn) adjustManualBtn.setAttribute('aria-expanded', 'true'); }
      setDist('~' + round + ' miles round trip', true);
      render();
    }).catch(function () { setDist('Couldn’t calculate — adjust manually.', false); });
  });
  if (adjustManualBtn) adjustManualBtn.addEventListener('click', function () {
    if (!manualWrap) return;
    var show = manualWrap.hidden; manualWrap.hidden = !show;
    adjustManualBtn.setAttribute('aria-expanded', show ? 'true' : 'false');
  });
  /* ---- inventory toggle (auto-fill / clear) + manual reveal ---- */
  function fillPreset(json) {
    var preset = {}; try { preset = JSON.parse(json || '{}'); } catch (e) {}
    inputs.forEach(function (i) { i.value = 0; });
    Object.keys(preset).forEach(function (id) { var el = document.getElementById(id); if (el) el.value = preset[id]; });
  }
  function syncPickerLabel() {
    if (tickManualBtn && picker) tickManualBtn.innerHTML = picker.hidden ? 'Or tick items manually →' : 'Hide item list ↑';
  }
  if (invToggle) invToggle.addEventListener('change', function () {
    if (invToggle.checked) {
      if (!selectedPreset) { var def = propBtns[2] || propBtns[0]; if (def) def.click(); }
      fillPreset(selectedPreset);
      if (picker) picker.hidden = false;
    } else {
      inputs.forEach(function (i) { i.value = 0; });
      if (picker) picker.hidden = true;                         // closing the toggle closes the item list
    }
    syncPickerLabel();
    render();
  });
  if (tickManualBtn) tickManualBtn.addEventListener('click', function () {
    if (!picker) return;
    picker.hidden = !picker.hidden;                             // toggle open/closed
    syncPickerLabel();
  });
  /* quick-term storage buttons set the days field */
  var durBtns = slice(root.querySelectorAll('.scalc-dur'));
  durBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      durBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
      btn.classList.add('is-sel'); btn.setAttribute('aria-pressed', 'true');
      if (daysInp) daysInp.value = parseInt(btn.getAttribute('data-days'), 10) || 0;
      render();
    });
  });

  /* ---- quote form -> /api/calculator (emails the estimate via Resend) ---- */
  function setQMsg(t, ok) { if (qMsg) { qMsg.textContent = t; qMsg.className = 'scalc-quote-msg' + (ok === true ? ' is-ok' : ok === false ? ' is-err' : ''); } }
  if (qForm) qForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (qForm.company && qForm.company.value) return;                 // honeypot
    if (!qForm.checkValidity()) { qForm.reportValidity(); return; }
    var fd = new FormData(qForm);
    var payload = { name: fd.get('name'), email: fd.get('email'), phone: fd.get('phone'), date: fd.get('date'), estimate: LAST };
    if (quoteBtn) quoteBtn.disabled = true;
    setQMsg('Sending your estimate…');
    fetch('/api/calculator', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }).catch(function () { return { ok: r.ok, d: {} }; }); })
      .then(function (res) {
        if (res.ok && res.d && res.d.ok) { qForm.reset(); setQMsg('Thank you! Your estimate is on its way to your inbox and our team — we’ll be in touch.', true); }
        else { setQMsg((res.d && res.d.error) || 'Sorry, we couldn’t send it just now — please call us instead.', false); if (quoteBtn) quoteBtn.disabled = false; }
      })
      .catch(function () { setQMsg('Sorry, we couldn’t send it just now — please call us instead.', false); if (quoteBtn) quoteBtn.disabled = false; });
  });
  if (milesInp) milesInp.addEventListener('input', render);
  if (daysInp) daysInp.addEventListener('input', function () {
    durBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
    render();
  });
  if (dateInp) dateInp.addEventListener('change', render);
  if (fromInp) fromInp.addEventListener('input', render);
  if (toInp) toInp.addEventListener('input', render);

  if (reset) reset.addEventListener('click', function () {
    inputs.forEach(function (i) { i.value = 0; });
    if (search) { search.value = ''; clearFilter(); showTab(tabs[0].dataset.target); }
    propBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
    selectedPreset = '';
    if (cuftInput) cuftInput.value = 0;
    if (cuftHint) cuftHint.innerHTML = DEFAULT_HINT;
    if (milesInp) milesInp.value = '';
    if (daysInp) daysInp.value = 28;
    if (dateInp) dateInp.value = '';
    if (fromInp) fromInp.value = '';
    if (toInp) toInp.value = '';
    var fn = document.getElementById('scalc-from-num'), tn = document.getElementById('scalc-to-num');
    if (fn) fn.value = ''; if (tn) tn.value = '';
    if (invToggle) invToggle.checked = false;
    if (picker) picker.hidden = true;
    syncPickerLabel();
    durBtns.forEach(function (b) { b.classList.remove('is-sel'); b.setAttribute('aria-pressed', 'false'); });
    if (manualWrap) manualWrap.hidden = true;
    if (distStatus) distStatus.textContent = '';
    if (invToggleLabel) invToggleLabel.textContent = 'Use our typical inventory list?';
    render();
  });

  if (tabs.length) showTab(tabs[0].dataset.target);
  applyMode();
})();
