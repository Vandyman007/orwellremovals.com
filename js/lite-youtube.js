/* Wolves Removals — lightweight, privacy-friendly YouTube facade.
 * Shows a self-hosted poster + play button; the YouTube iframe is only created
 * on click (no contact with YouTube until the visitor opts in). Plays muted.
 * Served from 'self'; iframe loads from youtube-nocookie.com (allowed in CSP).
 */
(function () {
  'use strict';
  var facades = document.querySelectorAll('.yt-facade');
  Array.prototype.forEach.call(facades, function (el) {
    function play() {
      if (el.classList.contains('yt-on')) return;
      el.classList.add('yt-on');
      var id = el.getAttribute('data-id');
      if (!id) return;
      var ifr = document.createElement('iframe');
      ifr.setAttribute('title', el.getAttribute('data-title') || 'Video');
      ifr.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture; fullscreen');
      ifr.setAttribute('allowfullscreen', '');
      ifr.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
        '?autoplay=1&mute=1&rel=0&modestbranding=1&playsinline=1';
      el.appendChild(ifr);
    }
    el.addEventListener('click', play);
  });
})();
