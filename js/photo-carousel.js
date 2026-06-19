/* Wolves Removals — photo-strip carousel
   Horizontal scroll-snap gallery with prev/next arrows. The slide nearest the
   centre of the viewport gets `.is-center`, which scales it up 20% vs siblings.
   Progressive enhancement: with JS off the strip is still a scrollable row. */
(function () {
  "use strict";

  function initCarousel(root) {
    var track = root.querySelector(".pstrip-track");
    var prev = root.querySelector(".pstrip-prev");
    var next = root.querySelector(".pstrip-next");
    if (!track) return;
    var slides = Array.prototype.slice.call(track.querySelectorAll(".pstrip-slide"));
    if (!slides.length) return;

    function slideCenter(s) { return s.offsetLeft + s.clientWidth / 2; }

    function update() {
      var viewCenter = track.scrollLeft + track.clientWidth / 2;
      var best = 0, bestDist = Infinity;
      for (var i = 0; i < slides.length; i++) {
        var d = Math.abs(slideCenter(slides[i]) - viewCenter);
        if (d < bestDist) { bestDist = d; best = i; }
      }
      for (var j = 0; j < slides.length; j++) {
        slides[j].classList.toggle("is-center", j === best);
      }
      var max = track.scrollWidth - track.clientWidth;
      if (prev) prev.disabled = track.scrollLeft <= 2;
      if (next) next.disabled = track.scrollLeft >= max - 2;
      return best;
    }

    function centerSlide(i) {
      i = Math.max(0, Math.min(slides.length - 1, i));
      var s = slides[i];
      track.scrollTo({
        left: s.offsetLeft - (track.clientWidth - s.clientWidth) / 2,
        behavior: "smooth"
      });
    }

    if (prev) prev.addEventListener("click", function () { centerSlide(update() - 1); });
    if (next) next.addEventListener("click", function () { centerSlide(update() + 1); });

    var ticking = false;
    track.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () { update(); ticking = false; });
    }, { passive: true });

    window.addEventListener("resize", function () { update(); });

    // Start centred on the middle image (no smooth scroll on first paint).
    var mid = Math.floor(slides.length / 2);
    var s = slides[mid];
    track.scrollLeft = s.offsetLeft - (track.clientWidth - s.clientWidth) / 2;
    update();
  }

  function init() {
    var nodes = document.querySelectorAll("[data-carousel]");
    for (var i = 0; i < nodes.length; i++) initCarousel(nodes[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
