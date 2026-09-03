/* Site-wide keyboard shortcuts and features */
(function() {
  var shortcuts = {
    '?': function() { showHelp(); },
    'h': function() { goTo('/'); },
    'v': function() { goTo('/videos/'); },
    's': function() { goTo('/streams/'); },
    'p': function() { goTo('/playlists/'); },
    'g': function() { goTo('/games/'); },
    'd': function() { goTo('/dashboard/'); },
    'i': function() { goTo('/history/'); },
    'a': function() { goTo('/about/'); },
  };

  function goTo(path) {
    var links = document.querySelectorAll('a[href="' + path + '"]');
    if (links.length) { links[0].click(); }
    else { window.location = path; }
  }

  function showHelp() {
    var existing = document.getElementById('kb-help');
    if (existing) { existing.remove(); return; }
    var overlay = document.createElement('div');
    overlay.id = 'kb-help';
    overlay.innerHTML = '<div class="kb-help-content"><h2>Keyboard Shortcuts</h2><table><tr><td><kbd>?</kbd></td><td>Toggle this help</td></tr><tr><td><kbd>H</kbd></td><td>Home</td></tr><tr><td><kbd>V</kbd></td><td>Videos</td></tr><tr><td><kbd>S</kbd></td><td>Streams</td></tr><tr><td><kbd>P</kbd></td><td>Playlists</td></tr><tr><td><kbd>G</kbd></td><td>Games</td></tr><tr><td><kbd>D</kbd></td><td>Dashboard</td></tr><tr><td><kbd>I</kbd></td><td>History</td></tr><tr><td><kbd>A</kbd></td><td>About</td></tr><tr><td><kbd>Esc</kbd></td><td>Close modals / help</td></tr></table><p class="kb-hint">Press <kbd>?</kbd> again to close</p></div>';
    overlay.onclick = function(e) { if (e.target === overlay) overlay.remove(); };
    document.body.appendChild(overlay);
  }

  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    var key = e.key.toLowerCase();
    if (key === 'escape') {
      var modals = document.querySelectorAll('.modal.open');
      modals.forEach(function(m) {
        var close = m.querySelector('.modal-close');
        if (close) close.click();
      });
      return;
    }
    if (shortcuts[key]) {
      e.preventDefault();
      shortcuts[key]();
    }
  });
})();

/* Random video (visible cards only, so series filters are respected) */
function randomVideo() {
  var all = document.querySelectorAll('[data-video-id]');
  var cards = [];
  Array.prototype.forEach.call(all, function(c) {
    if (c.offsetParent !== null) cards.push(c);
  });
  if (!cards.length) return;
  var pick = cards[Math.floor(Math.random() * cards.length)];
  if (typeof openPlayer === 'function') {
    openPlayer(pick);
  } else {
    var id = pick.getAttribute('data-video-id');
    window.open('https://www.youtube.com/watch?v=' + id, '_blank');
  }
}

/* Toggle More dropdown for filter bar */
function toggleMoreFilters() {
  var dd = document.getElementById('filter-more-dropdown');
  if (!dd) return;
  dd.classList.toggle('open');
}

/* Close More dropdown on outside click */
document.addEventListener('click', function(e) {
  var wrap = document.querySelector('.filter-more-wrap');
  var dd = document.getElementById('filter-more-dropdown');
  if (wrap && dd && dd.classList.contains('open') && !wrap.contains(e.target)) {
    dd.classList.remove('open');
  }
});

/* Series filter */
function filterSeries(btn) {
  // Close the More dropdown if open
  var dd = document.getElementById('filter-more-dropdown');
  if (dd) dd.classList.remove('open');

  // Remove pagination: reveal all, then remove the button
  Array.prototype.forEach.call(document.querySelectorAll('.paged-hidden'), function(el) {
    el.classList.remove('paged-hidden');
    el.style.display = '';
  });
  var loadBtn = document.querySelector('.load-more-btn');
  if (loadBtn) loadBtn.style.display = 'none';

  var grid = document.getElementById('video-grid');
  if (!grid) return;
  var name = btn ? btn.getAttribute('data-series-name') : null;
  var cards = grid.querySelectorAll('.video-card');
  document.querySelectorAll('.filter-btn').forEach(function(b) { b.classList.remove('active'); });
  if (btn) btn.classList.add('active');
  cards.forEach(function(c) {
    var series = c.getAttribute('data-series');
    if (!name || series === name) {
      c.style.display = '';
    } else {
      c.style.display = 'none';
    }
  });
}

/* Chapter parsing */
function parseChapters(description) {
  if (!description) return [];
  var lines = description.split('\n');
  var chapters = [];
  var re = /^(?:(\d{1,2}):(\d{2})(?::(\d{2}))?\s*[-–]\s*(.+))/;
  lines.forEach(function(line) {
    var m = line.trim().match(re);
    if (m) {
      var secs = parseInt(m[1]) * 60 + parseInt(m[2]);
      if (m[3]) secs = parseInt(m[1]) * 3600 + parseInt(m[2]) * 60 + parseInt(m[3]);
      chapters.push({ time: secs, label: m[4] });
    }
  });
  return chapters;
}

/* "Watch next" - find next chronological video in same series */
function findWatchNext(currentCard) {
  var series = currentCard ? currentCard.getAttribute('data-series') : null;
  if (!series) return null;
  var cards = Array.from(document.querySelectorAll('[data-series="' + series + '"]'));
  cards.sort(function(a, b) {
    return new Date(a.getAttribute('data-published')) - new Date(b.getAttribute('data-published'));
  });
  var idx = cards.indexOf(currentCard);
  return (idx >= 0 && idx < cards.length - 1) ? cards[idx + 1] : null;
}

/* Relative time display */
document.addEventListener('DOMContentLoaded', function() {
  var els = document.querySelectorAll('.reltime');
  if (!els.length) return;
  els.forEach(function(el) {
    var dt = el.getAttribute('datetime');
    if (!dt) return;
    var then = new Date(dt);
    var now = new Date();
    var diff = now - then;
    var seconds = Math.floor(diff / 1000);
    var minutes = Math.floor(seconds / 60);
    var hours = Math.floor(minutes / 60);
    var days = Math.floor(hours / 24);
    var weeks = Math.floor(days / 7);
    var months = Math.floor(days / 30);
    var years = Math.floor(days / 365);
    var rel;
    if (seconds < 60) rel = 'just now';
    else if (minutes < 60) rel = minutes + 'm ago';
    else if (hours < 24) rel = hours + 'h ago';
    else if (days < 7) rel = days + 'd ago';
    else if (weeks < 5) rel = weeks + 'w ago';
    else if (months < 12) rel = months + 'mo ago';
    else rel = years + 'y ago';
el.textContent = '\u00b7 ' + rel;
  });
});

/* Live stream auto-detection */
(function() {
  var twitchPlayer = null;
  var twitchLive = false;
  var currentPlatform = 'twitch';
  var CHECK_MS = 5 * 60 * 1000;
  var onlineFired = false;

  function getParents() {
    var hosts = ['localhost', 'skiyliansoftware.github.io', 'skiyliansoftware.com'];
    if (window.location.hostname) hosts.push(window.location.hostname);
    return hosts;
  }

  function initTwitch() {
    if (typeof Twitch === 'undefined') {
      var s = document.createElement('script');
      s.src = 'https://player.twitch.tv/js/embed/v1.js';
      s.onload = createTwitchPlayer;
      s.onerror = function() { console.warn('Twitch embed failed to load'); };
      document.head.appendChild(s);
    } else {
      createTwitchPlayer();
    }
  }

  function createTwitchPlayer() {
    var c = document.getElementById('twitch-player-container');
    if (!c) return;
    try {
      twitchPlayer = new Twitch.Player('twitch-player-container', {
        channel: 'skiylia',
        width: '100%',
        height: 480,
        autoplay: true,
        parent: getParents(),
      });

      twitchPlayer.addEventListener(Twitch.Player.ONLINE, function() {
        onlineFired = true;
        twitchLive = true;
        showLive('twitch');
      });

      twitchPlayer.addEventListener(Twitch.Player.OFFLINE, function() {
        twitchLive = false;
        if (currentPlatform === 'twitch') checkOffline();
      });

      setTimeout(function() {
        if (!onlineFired) {
          twitchLive = false;
        }
      }, 8000);
    } catch (e) {
      console.warn('Twitch player init failed:', e);
    }
  }

  function showLive(platform) {
    var off = document.getElementById('offline-panel');
    var live = document.getElementById('live-embed');
    if (off) off.style.display = 'none';
    if (live) live.style.display = 'block';
    if (platform) switchLivePlatform(platform);
  }

  function hideLive() {
    var off = document.getElementById('offline-panel');
    var live = document.getElementById('live-embed');
    if (off) off.style.display = '';
    if (live) live.style.display = 'none';
  }

  function checkOffline() {
    if (!twitchLive) hideLive();
  }

  window.switchLivePlatform = function(platform) {
    currentPlatform = platform;
    document.querySelectorAll('.live-tab').forEach(function(b) {
      b.classList.toggle('active', b.dataset.platform === platform);
    });
    document.getElementById('twitch-player-container').style.display =
      platform === 'twitch' ? '' : 'none';
    document.getElementById('youtube-player-container').style.display =
      platform === 'youtube' ? '' : 'none';
    if (platform === 'youtube') refreshYouTube();
  };

  function refreshYouTube() {
    var f = document.getElementById('youtube-live-iframe');
    if (f) f.src = 'https://www.youtube.com/embed/live_stream?channel=UC4s4eXHuzj7OxwJXgiZgAYw&autoplay=1&_=' + Date.now();
  }

  document.addEventListener('DOMContentLoaded', function() {
    initTwitch();
    setInterval(refreshYouTube, CHECK_MS);
  });
})();

/* Balanced ternary age on the home page */
(function() {
  function toBalancedTernary(n) {
    if (n === 0) return '0';
    var digits = [];
    while (n > 0) {
      var r = n % 3;
      n = Math.floor(n / 3);
      if (r === 2) { digits.unshift('1'); n += 1; }
      else if (r === 1) { digits.unshift('1'); }
      else { digits.unshift('0'); }
    }
    return digits.join('') + ' (balanced ternary)';
  }
  document.addEventListener('DOMContentLoaded', function() {
    var el = document.getElementById('ternary-age');
    if (!el) return;
    var start = el.getAttribute('data-start');
    if (!start) return;
    var t0 = new Date(start).getTime();
    var days = Math.floor((Date.now() - t0) / 86400000);
    var val = document.getElementById('ternary-age-value');
    if (val) val.textContent = toBalancedTernary(days + 1);
  });
})();


