/* Site-wide keyboard shortcuts and features */
(function() {
  var shortcuts = {
    '?': function() { showHelp(); },
    'h': function() { goTo('/'); },
    'v': function() { goTo('/videos/'); },
    's': function() { goTo('/streams/'); },
    'p': function() { goTo('/playlists/'); },
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
    overlay.innerHTML = '<div class="kb-help-content"><h2>Keyboard Shortcuts</h2><table><tr><td><kbd>?</kbd></td><td>Toggle this help</td></tr><tr><td><kbd>H</kbd></td><td>Home</td></tr><tr><td><kbd>V</kbd></td><td>Videos</td></tr><tr><td><kbd>S</kbd></td><td>Streams</td></tr><tr><td><kbd>P</kbd></td><td>Playlists</td></tr><tr><td><kbd>A</kbd></td><td>About</td></tr><tr><td><kbd>Esc</kbd></td><td>Close modals / help</td></tr></table><p class="kb-hint">Press <kbd>?</kbd> again to close</p></div>';
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

/* Random video */
function randomVideo() {
  var cards = document.querySelectorAll('[data-video-id]');
  if (!cards.length) return;
  var pick = cards[Math.floor(Math.random() * cards.length)];
  if (typeof openPlayer === 'function') {
    openPlayer(pick);
  } else {
    var id = pick.getAttribute('data-video-id');
    window.open('https://www.youtube.com/watch?v=' + id, '_blank');
  }
}

/* Series filter */
function filterSeries(btn, name) {
  var grid = document.getElementById('video-grid');
  if (!grid) return;
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

/* "Watch next" - find next video in same series */
function findWatchNext(currentCard) {
  var series = currentCard ? currentCard.getAttribute('data-series') : null;
  if (!series) return null;
  var cards = Array.from(document.querySelectorAll('[data-series="' + series + '"]'));
  var idx = cards.indexOf(currentCard);
  return (idx >= 0 && idx < cards.length - 1) ? cards[idx + 1] : null;
}

/* Parallax stars on scroll */
var scrollPos = 0;
window.addEventListener('scroll', function() {
  scrollPos = window.scrollY;
  var bg = document.body;
  var offset = scrollPos * 0.05;
  bg.style.setProperty('--star-offset', offset + 'px');
});

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