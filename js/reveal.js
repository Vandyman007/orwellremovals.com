(function () {
  var els = [].slice.call(document.querySelectorAll('.reveal-lr, .reveal-left, .reveal-right, .reveal-roll, .reveal-swipe'));
  if (!els.length) return;
  // Arm staggered containers immediately (so without JS their items just show, no hidden state).
  [].slice.call(document.querySelectorAll('.reveal-roll, .reveal-swipe')).forEach(function (e) { e.classList.add('armed'); });
  if (!('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('in'); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  els.forEach(function (e) { io.observe(e); });
})();
