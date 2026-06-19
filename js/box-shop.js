/* Box Shop — quantity steppers on product cards drive a live sticky basket (item
   thumbnails, mini steppers, remove, count badge, subtotal). On submit the order is
   posted to /api/boxshop which emails both Wolves and the customer. Progressive
   enhancement: products + prices read fine without JS; ordering needs JS. */
(function () {
  var form = document.getElementById('bs-form');
  var itemsEl = document.querySelector('[data-bs-items]');
  var totalEls = document.querySelectorAll('[data-bs-total]');   // basket panel + mobile bar
  var countEls = document.querySelectorAll('[data-bs-count]');
  var msg = document.querySelector('[data-bs-msg]');
  if (!form || !itemsEl) return;

  // Mobile cart drawer (no-op on desktop, where the basket is a static sidebar).
  var drawer = document.querySelector('.bs-drawer');
  var overlay = document.querySelector('[data-bs-overlay]');
  function openCart() { if (drawer) drawer.classList.add('is-open'); if (overlay) overlay.classList.remove('hidden'); document.body.classList.add('bs-noscroll'); }
  function closeCart() { if (drawer) drawer.classList.remove('is-open'); if (overlay) overlay.classList.add('hidden'); document.body.classList.remove('bs-noscroll'); }
  Array.prototype.forEach.call(document.querySelectorAll('[data-bs-open]'), function (b) { b.addEventListener('click', openCart); });
  Array.prototype.forEach.call(document.querySelectorAll('[data-bs-close]'), function (b) { b.addEventListener('click', closeCart); });
  if (overlay) overlay.addEventListener('click', closeCart);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeCart(); });

  var inputs = Array.prototype.slice.call(document.querySelectorAll('[data-bs-product]'));
  var byId = {};
  inputs.forEach(function (inp) { byId[inp.getAttribute('data-bs-product')] = inp; });

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function qtyOf(inp) { var n = parseInt(inp.value, 10); return (isNaN(n) || n < 0) ? 0 : n; }
  function iconFor(id) {
    var el = document.querySelector('[data-bs-card="' + (window.CSS && CSS.escape ? CSS.escape(id) : id) + '"] .bs-icon');
    return el ? el.innerHTML : '';
  }
  function setQty(id, n) { var inp = byId[id]; if (!inp) return; inp.value = Math.max(0, n); update(); }

  function selected() {
    var out = [];
    inputs.forEach(function (inp) {
      var n = qtyOf(inp);
      if (n > 0) out.push({
        id: inp.getAttribute('data-bs-product'),
        name: inp.getAttribute('data-bs-name'),
        price: parseFloat(inp.getAttribute('data-bs-price')) || 0,
        qty: n
      });
    });
    return out;
  }

  function update() {
    inputs.forEach(function (inp) {
      var card = inp.closest('[data-bs-card]');
      if (card) card.classList.toggle('bs-active', qtyOf(inp) > 0);
    });
    var items = selected(), total = 0, count = 0, html = '';
    if (!items.length) {
      html = '<p class="text-darkgrey text-sm py-8 text-center">Your basket is empty.<br>Add a kit or some materials to get started.</p>';
    } else {
      items.forEach(function (x) {
        var lt = x.price * x.qty; total += lt; count += x.qty;
        html +=
          '<div class="flex gap-3 py-3 border-b border-border last:border-b-0">' +
            '<div class="w-14 h-14 rounded-lg bg-white border border-border flex items-center justify-center shrink-0 text-darkgrey p-2 overflow-hidden"><span class="w-full h-full block">' + iconFor(x.id) + '</span></div>' +
            '<div class="flex-1 min-w-0">' +
              '<p class="font-semibold text-black text-sm leading-snug">' + esc(x.name) + '</p>' +
              '<p class="text-xs text-darkgrey">&pound;' + x.price.toFixed(2) + ' each</p>' +
              '<div class="inline-flex items-center mt-1.5 rounded-full border border-border">' +
                '<button type="button" data-bs-mini="-1" data-id="' + esc(x.id) + '" aria-label="Remove one ' + esc(x.name) + '" class="w-7 h-7 flex items-center justify-center text-darkgrey hover:text-black">&minus;</button>' +
                '<span class="w-7 text-center text-sm font-semibold text-black">' + x.qty + '</span>' +
                '<button type="button" data-bs-mini="1" data-id="' + esc(x.id) + '" aria-label="Add one ' + esc(x.name) + '" class="w-7 h-7 flex items-center justify-center text-darkgrey hover:text-black">+</button>' +
              '</div>' +
            '</div>' +
            '<div class="text-right shrink-0"><p class="font-bold text-black">&pound;' + lt.toFixed(2) + '</p>' +
              '<button type="button" data-bs-remove="' + esc(x.id) + '" class="text-xs text-darkgrey hover:text-black hover:underline mt-1">Remove</button></div>' +
          '</div>';
      });
    }
    itemsEl.innerHTML = html;
    Array.prototype.forEach.call(totalEls, function (el) { el.innerHTML = '&pound;' + total.toFixed(2); });
    Array.prototype.forEach.call(countEls, function (el) { el.textContent = count; });
    return { items: items, total: total, count: count };
  }

  // Card steppers.
  Array.prototype.forEach.call(document.querySelectorAll('[data-bs-step]'), function (btn) {
    btn.addEventListener('click', function () {
      var card = btn.closest('[data-bs-card]');
      var inp = card && card.querySelector('[data-bs-product]');
      if (!inp) return;
      inp.value = Math.max(0, qtyOf(inp) + parseInt(btn.getAttribute('data-bs-step'), 10));
      update();
    });
  });
  inputs.forEach(function (inp) {
    inp.addEventListener('input', function () { inp.value = inp.value.replace(/[^0-9]/g, ''); update(); });
    inp.addEventListener('blur', function () { if (inp.value === '') inp.value = 0; update(); });
  });

  // Basket mini-steppers + remove (event-delegated).
  itemsEl.addEventListener('click', function (e) {
    var mini = e.target.closest('[data-bs-mini]');
    if (mini) { var id = mini.getAttribute('data-id'); setQty(id, qtyOf(byId[id]) + parseInt(mini.getAttribute('data-bs-mini'), 10)); return; }
    var rm = e.target.closest('[data-bs-remove]');
    if (rm) setQty(rm.getAttribute('data-bs-remove'), 0);
  });

  update();

  // Category + search filter — a product shows only if it matches the active
  // category AND the search query (all typed words must appear).
  var pills = document.querySelectorAll('[data-bs-filter]');
  var prodCards = document.querySelectorAll('[data-bs-cat]');
  var searchEl = document.getElementById('bs-search');
  var noRes = document.querySelector('[data-bs-noresults]');
  var activeCat = 'all';
  function runFilter() {
    var tokens = (searchEl ? searchEl.value : '').trim().toLowerCase().split(/\s+/).filter(Boolean);
    var n = 0;
    Array.prototype.forEach.call(prodCards, function (c) {
      var catOk = (activeCat === 'all' || c.getAttribute('data-bs-cat') === activeCat);
      var txt = c.getAttribute('data-bs-search') || '';
      var qOk = !tokens.length || tokens.every(function (t) { return txt.indexOf(t) > -1; });
      var ok = catOk && qOk;
      c.style.display = ok ? '' : 'none';
      if (ok) n++;
    });
    if (noRes) noRes.classList.toggle('hidden', n > 0);
  }
  Array.prototype.forEach.call(pills, function (p) {
    p.addEventListener('click', function () {
      activeCat = p.getAttribute('data-bs-filter');
      Array.prototype.forEach.call(pills, function (q) { q.classList.toggle('bs-pill-on', q === p); });
      runFilter();
    });
  });
  if (searchEl) searchEl.addEventListener('input', runFilter);
  Array.prototype.forEach.call(document.querySelectorAll('[data-bs-clear]'), function (b) {
    b.addEventListener('click', function () {
      if (searchEl) searchEl.value = '';
      activeCat = 'all';
      Array.prototype.forEach.call(pills, function (q) { q.classList.toggle('bs-pill-on', q.getAttribute('data-bs-filter') === 'all'); });
      runFilter();
    });
  });

  function setMsg(t, ok) {
    msg.textContent = t;
    msg.className = 'text-sm font-semibold ' + (ok === true ? 'text-[#262626]' : ok === false ? 'text-[#c0392b]' : 'text-darkgrey');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var order = update();
    if (!order.items.length) { setMsg('Your basket is empty — add a kit or some materials first.', false); return; }
    var fd = new FormData(form);
    if (!fd.get('name') || !fd.get('email')) { setMsg('Please add your name and email so we can confirm your order.', false); return; }
    var payload = {
      items: order.items, total: order.total,
      name: fd.get('name'), email: fd.get('email'), phone: fd.get('phone'),
      fulfilment: fd.get('fulfilment'), address: fd.get('address'), notes: fd.get('notes')
    };
    var btn = form.querySelector('[type=submit]');
    btn.disabled = true; setMsg('Sending your order…');
    fetch('/api/boxshop', {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload)
    }).then(function (r) {
      return r.json().then(function (d) { return { ok: r.ok, d: d }; }).catch(function () { return { ok: r.ok, d: {} }; });
    }).then(function (res) {
      if (res.ok && res.d && res.d.ok) {
        form.reset();
        inputs.forEach(function (i) { i.value = 0; });
        update();
        setMsg('Thank you! Your order has been sent and a copy is on its way to your email. We’ll be in touch to confirm.', true);
      } else {
        setMsg((res.d && res.d.error) || 'Sorry, we couldn’t send your order just now — please call us and we’ll sort it.', false);
        btn.disabled = false;
      }
    }).catch(function () {
      setMsg('Sorry, we couldn’t send your order just now — please call us and we’ll sort it.', false);
      btn.disabled = false;
    });
  });
})();
