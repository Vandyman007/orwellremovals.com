/* Step-by-step process — mobile swipe carousel with dot indicators.
   Syncs the active dot to the most-visible step and lets dots scroll to a step. */
(function () {
  function init() {
    document.querySelectorAll('[data-proc]').forEach(function (wrap) {
      var track = wrap.querySelector('.proc-scroll');
      var dots = Array.prototype.slice.call(wrap.querySelectorAll('.proc-dot'));
      if (!track || !dots.length) return;
      var steps = Array.prototype.slice.call(track.querySelectorAll('.proc-step'));

      function setActive(i) {
        dots.forEach(function (d, j) { d.classList.toggle('is-active', j === i); });
      }

      dots.forEach(function (d, i) {
        d.addEventListener('click', function () {
          if (steps[i]) steps[i].scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        });
      });

      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting && e.intersectionRatio >= 0.55) {
              var i = steps.indexOf(e.target);
              if (i >= 0) setActive(i);
            }
          });
        }, { root: track, threshold: [0.55] });
        steps.forEach(function (s) { io.observe(s); });
      } else {
        // Fallback: estimate active step from scroll position.
        track.addEventListener('scroll', function () {
          var i = Math.round(track.scrollLeft / (track.scrollWidth - track.clientWidth) * (steps.length - 1)) || 0;
          setActive(Math.max(0, Math.min(steps.length - 1, i)));
        }, { passive: true });
      }
      setActive(0);
    });
  }
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
