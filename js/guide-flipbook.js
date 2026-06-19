/**
 * Essential Moving Guide — flipbook viewer (home page).
 *
 * StPageFlip-powered, A4 portrait pages. On mobile, swipe + corner-grab +
 * click-to-flip are disabled — navigation is via the Prev/Next buttons only.
 * Desktop keeps full corner-flip interaction, with a soft page-turn sound.
 */
(function () {
  'use strict';

  var container = document.getElementById('guide-flipbook');
  if (!container || !window.St || !window.St.PageFlip) return;

  var TOTAL = 16;
  var isMobile = window.matchMedia('(max-width: 768px)').matches;
  var ver = container.getAttribute('data-ver');
  var q = ver ? ('?v=' + ver) : '';

  for (var i = 1; i <= TOTAL; i++) {
    var pn = String(i).padStart(2, '0');
    var pg = document.createElement('div');
    pg.className = 'guide-page';
    pg.innerHTML = '<img src="/images/guide-pages/page-' + pn + '.jpg' + q + '" ' +
                   'alt="Wolves Removals essential moving guide, page ' + i + ' of ' + TOTAL + '" ' +
                   'loading="' + (i <= 2 ? 'eager' : 'lazy') + '">';
    container.appendChild(pg);
  }

  var flip = new St.PageFlip(container, {
    width: 480,
    height: 679,          // A4 portrait ratio (1 : 1.414)
    size: 'stretch',
    minWidth: 260,
    maxWidth: 620,
    minHeight: 368,
    maxHeight: 877,
    drawShadow: true,
    flippingTime: 600,
    usePortrait: true,
    startZIndex: 0,
    autoSize: true,
    maxShadowOpacity: 0.4,
    showCover: false,
    mobileScrollSupport: true,
    swipeDistance: isMobile ? 99999 : 30,
    showPageCorners: !isMobile,
    disableFlipByClick: isMobile,
    useMouseEvents: !isMobile,
  });
  flip.loadFromHTML(container.querySelectorAll('.guide-page'));

  // Page-turn sound (synthesised paper rustle via Web Audio)
  var AudioCtx = window.AudioContext || window.webkitAudioContext;
  var audioCtx = null;
  function ensureAudio() {
    if (!audioCtx && AudioCtx) { try { audioCtx = new AudioCtx(); } catch (e) {} }
    return audioCtx;
  }
  function playFlipSound() {
    var ctx = ensureAudio();
    if (!ctx) return;
    if (ctx.state === 'suspended') ctx.resume();
    var now = ctx.currentTime;
    var bufSize = ctx.sampleRate * 0.25;
    var buffer = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    var data = buffer.getChannelData(0);
    for (var i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1) * 0.5;
    var src = ctx.createBufferSource();
    src.buffer = buffer;
    var filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.Q.value = 1.2;
    filter.frequency.setValueAtTime(4500, now);
    filter.frequency.exponentialRampToValueAtTime(800, now + 0.20);
    var gain = ctx.createGain();
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(0.18, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);
    src.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
    src.start(now); src.stop(now + 0.25);
  }
  flip.on('flip', playFlipSound);
  container.addEventListener('click', ensureAudio, { once: true });
  container.addEventListener('touchstart', ensureAudio, { once: true, passive: true });

  var prevBtn = document.getElementById('guide-prev');
  var nextBtn = document.getElementById('guide-next');
  var pageInd = document.getElementById('guide-page-indicator');
  if (prevBtn) prevBtn.addEventListener('click', function () { flip.flipPrev(); });
  if (nextBtn) nextBtn.addEventListener('click', function () { flip.flipNext(); });
  function updateIndicator() {
    if (!pageInd) return;
    pageInd.textContent = 'Page ' + (flip.getCurrentPageIndex() + 1) + ' of ' + TOTAL;
  }
  flip.on('flip', updateIndicator);
  updateIndicator();

  var hint = document.querySelector('.guide-flipbook-hint');
  if (hint) {
    hint.textContent = isMobile
      ? 'Use the Prev / Next buttons to turn the page.'
      : 'Click or grab the page corners to turn — a soft page-turn sound plays as you flick.';
  }
})();
