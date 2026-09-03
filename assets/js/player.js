/*
 * Shared video/VOD player modal and page behaviour.
 * Loaded on any page that includes the video-modal.
 * All functions are global so inline onclick handlers can call them.
 */
(function() {
  var _openEl = null;
  var _lastFocused = null;

  function q(sel) { return document.querySelector(sel); }
  function qa(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }

  window.formattedDuration = function(secs) {
    var h = Math.floor(secs / 3600);
    var m = Math.floor((secs % 3600) / 60);
    var s = secs % 60;
    if (h > 0) return h + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
    return m + ':' + String(s).padStart(2, '0');
  };

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.appendChild(document.createTextNode(t == null ? '' : String(t)));
    return d.innerHTML;
  }

  function linkify(t) {
    return t.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
  }

  function parseChapters(description) {
    if (!description) return [];
    var chapters = [];
    var re = /^(?:(\d{1,2}):(\d{2})(?::(\d{2}))?\s*[-–]\s*(.+))/;
    String(description).split('\n').forEach(function(line) {
      var m = line.trim().match(re);
      if (m) {
        var secs = parseInt(m[1], 10) * 60 + parseInt(m[2], 10);
        if (m[3]) secs = parseInt(m[1], 10) * 3600 + parseInt(m[2], 10) * 60 + parseInt(m[3], 10);
        chapters.push({ time: secs, label: m[4] });
      }
    });
    return chapters;
  }

  function seriesSiblings(card) {
    var series = card ? card.getAttribute('data-series') : null;
    if (!series) return [];
    return qa('[data-series="' + series + '"]')
      .filter(function(c) { return c !== card; });
  }

  function findWatchNext(card) {
    if (!card) return null;
    var series = card.getAttribute('data-series');
    if (!series) return null;
    var cards = qa('[data-series="' + series + '"]').sort(function(a, b) {
      return new Date(a.getAttribute('data-published')) - new Date(b.getAttribute('data-published'));
    });
    var idx = cards.indexOf(card);
    return (idx >= 0 && idx < cards.length - 1) ? cards[idx + 1] : null;
  }

  function renderMeta(el) {
    var box = document.getElementById('modal-meta');
    if (!box) return;
    var parts = [];
    var published = el.getAttribute('data-published');
    var views = parseInt(el.getAttribute('data-views')) || 0;
    var duration = parseInt(el.getAttribute('data-duration')) || 0;
    if (published) parts.push('<span class="meta-date"><time datetime="' + published + '">' + new Date(published).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) + '</time></span>');
    if (views > 0) parts.push('<span class="meta-views">' + Number(views).toLocaleString() + ' views</span>');
    if (duration > 0) parts.push('<span class="meta-duration">' + formattedDuration(duration) + '</span>');
    // Engagement rate: (likes + comments) / views
    var likes = parseInt(el.getAttribute('data-likes')) || 0;
    var comments2 = parseInt(el.getAttribute('data-comments')) || 0;
    if (views > 0 && (likes > 0 || comments2 > 0)) {
      var eng = ((likes + comments2) / views * 100).toFixed(1);
      parts.push('<span class="meta-engagement" title="(likes + comments) / views">' + eng + '% engagement</span>');
    }
    box.innerHTML = parts.join(' &middot; ');
    box.style.display = parts.length ? '' : 'none';
  }

  function renderLinks(el) {
    var box = document.getElementById('modal-series-link');
    if (!box) return;
    var parts = [];
    var series = el.getAttribute('data-series');
    var game = el.getAttribute('data-game');
    var episode = el.getAttribute('data-episode');
    var gameSlug = el.getAttribute('data-game-slug');
    var seriesSlug = el.getAttribute('data-series-slug');
    if (series) {
      var seriesUrl = seriesSlug ? '/series/' + seriesSlug + '/' : '/videos/';
      parts.push('<a href="' + seriesUrl + '" class="series-badge-link">' + escapeHtml(series) + '</a>');
    }
    if (game) {
      var gameUrl = gameSlug ? '/games/' + gameSlug + '/' : '/games/';
      parts.push('<a href="' + gameUrl + '" class="game-badge-link">' + escapeHtml(game) + '</a>');
    }
    if (episode) parts.push('<span class="ep-badge">Episode ' + escapeHtml(episode) + '</span>');
    box.innerHTML = parts.join(' ');
    box.style.display = parts.length ? '' : 'none';
  }

  function renderDescription(desc) {
    var box = document.getElementById('modal-description');
    if (!box) return;
    if (desc) {
      var text = String(desc);
      // Jekyll's | escape filter turns newlines into literal \n sequences.
      // Also handle HTML line-breaks if they made it through.
      text = text.replace(/\\n/g, '\n').replace(/<br\s*\/?>/gi, '\n');
      // Format chapter-style timestamps as clickable chips
      text = text.replace(/(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–]\s*/g,
        '<span class="chap-inline" data-chap-time="$1">$1 - </span>');
      box.innerHTML = '<div class="desc-text">' + linkify(escapeHtml(text).replace(/\n/g, '<br>')) + '</div>';
      box.style.display = '';
    } else {
      box.innerHTML = '';
      box.style.display = 'none';
    }
  }

  function renderChapters(id, desc) {
    var box = document.getElementById('modal-chapters');
    if (!box) return;
    var chips = parseChapters(desc);
    if (chips.length) {
      box.innerHTML = '<p class="chapters-label">Chapters</p>' + chips.map(function(c) {
        return '<span class="chapter-chip" data-start="' + c.time + '">' + escapeHtml(c.label) + '</span>';
      }).join('');
      box.style.display = '';
    } else {
      box.innerHTML = '';
      box.style.display = 'none';
    }
  }

  function renderWatchNext(card) {
    var box = document.getElementById('modal-next');
    if (!box) return;
    var next = findWatchNext(card);
    if (next) {
      var nid = next.getAttribute('data-video-id');
      var ntitle = next.getAttribute('data-title');
      box.innerHTML = '<p class="next-label">Up next</p><div class="next-card" data-watch-next="' + nid + '"><span class="next-title">' + escapeHtml(ntitle) + '</span></div>';
      box.style.display = '';
    } else {
      box.innerHTML = '';
      box.style.display = 'none';
    }
  }

  function renderSeriesMore(card) {
    var box = document.getElementById('modal-series-more');
    if (!box) return;
    var siblings = seriesSiblings(card);
    if (siblings.length) {
      var html = '<p class="series-more-label">More from this series</p><div class="series-more-grid">';
      siblings.slice(0, 6).forEach(function(c) {
        var img = c.querySelector('img');
        var src = img ? img.getAttribute('src') : '';
        var id = c.getAttribute('data-video-id');
        var t = c.getAttribute('data-title') || '';
        html += '<div class="series-more-item" data-video-id="' + id + '" title="' + escapeHtml(t) + '">';
        if (src) html += '<img src="' + src + '" alt="" loading="lazy">';
        html += '</div>';
      });
      html += '</div>';
      box.innerHTML = html;
      box.style.display = '';
    } else {
      box.innerHTML = '';
      box.style.display = 'none';
    }
  }

  function setIframe(id, start) {
    var wrap = document.getElementById('player-wrap');
    if (!wrap) return;
    var src = 'https://www.youtube.com/embed/' + id + '?autoplay=1';
    if (start) src += '&start=' + start;
    wrap.innerHTML = '<iframe width="100%" height="100%" src="' + src + '" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
  }

  window.openClip = function(el) {
    var cid = el.getAttribute('data-clip-id');
    if (!cid) return;
    _openEl = null; // clips aren't in the [data-video-id] series set
    _lastFocused = document.activeElement;

    var wrap = document.getElementById('player-wrap');
    if (wrap) {
      wrap.innerHTML = '<iframe width="100%" height="100%" src="https://clips.twitch.tv/embed?clip=' + cid + '&parent=' + window.location.hostname + '&autoplay=true" frameborder="0" allow="autoplay; encrypted-media; fullscreen" allowfullscreen></iframe>';
    }

    var title = el.getAttribute('data-title') || '';
    var titleNode = document.getElementById('modal-title');
    if (titleNode) titleNode.textContent = title;

    var link = document.getElementById('modal-link');
    if (link) {
      link.href = 'https://clips.twitch.tv/' + cid;
      link.textContent = 'Watch on Twitch';
    }

    var metaBox = document.getElementById('modal-meta');
    if (metaBox) {
      var parts = [];
      var views = parseInt(el.getAttribute('data-views'), 10) || 0;
      if (views > 0) parts.push('<span class="meta-views">' + Number(views).toLocaleString() + ' views</span>');
      var game = el.getAttribute('data-game');
      if (game) parts.push('<span class="meta-views">' + escapeHtml(game) + '</span>');
      metaBox.innerHTML = parts.join(' &middot; ');
      metaBox.style.display = parts.length ? '' : 'none';
    }

    ['modal-description', 'modal-chapters', 'modal-next', 'modal-series-more'].forEach(function(sel) {
      var box = document.getElementById(sel);
      if (box) { box.innerHTML = ''; box.style.display = 'none'; }
    });
    var seriesBox = document.getElementById('modal-series-link');
    if (seriesBox) { seriesBox.innerHTML = ''; seriesBox.style.display = 'none'; }

    var modal = document.getElementById('video-modal');
    if (modal) {
      modal.classList.add('open');
      var close = modal.querySelector('.modal-close');
      if (close) close.focus();
    }
  };

  window.openPlayer = function(el) {
    _openEl = el;
    var id = el.getAttribute('data-video-id');
    _lastFocused = document.activeElement;
    setIframe(id, 0);

    var title = el.getAttribute('data-title') || '';
    var titleNode = document.getElementById('modal-title');
    if (titleNode) titleNode.textContent = title;

    var link = document.getElementById('modal-link');
    if (link) {
      var platform = el.getAttribute('data-platform');
      if (platform === 'twitch') {
        link.href = el.getAttribute('data-url') || 'https://www.twitch.tv/videos/' + id;
        link.textContent = 'Watch on Twitch';
      } else {
        link.href = 'https://www.youtube.com/watch?v=' + id;
        link.textContent = 'Watch on YouTube';
      }
    }

    renderMeta(el);
    renderLinks(el);
    var desc = el.getAttribute('data-description') || '';
    renderDescription(desc);
    renderChapters(id, desc);
    renderWatchNext(el);
    renderSeriesMore(el);

    var modal = document.getElementById('video-modal');
    if (modal) {
      modal.classList.add('open');
      var close = modal.querySelector('.modal-close');
      if (close) close.focus();
    }
  };

  window.closePlayer = function() {
    var wrap = document.getElementById('player-wrap');
    if (wrap) wrap.innerHTML = '';
    var modal = document.getElementById('video-modal');
    if (modal) modal.classList.remove('open');
    var chapters = document.getElementById('modal-chapters');
    if (chapters) chapters.innerHTML = '';
    var desc = document.getElementById('modal-description');
    if (desc) desc.innerHTML = '';
    _openEl = null;
    if (_lastFocused && _lastFocused.focus) _lastFocused.focus();
    _lastFocused = null;
  };

  /* Sort controls (videos + playlists pages) */
  window.sortGrid = function(btn, mode) {
    qa('.sort-btn').forEach(function(b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');
    var grid = document.getElementById('video-grid');
    if (!grid) return;

    // Reset pagination: reveal all cards
    if (grid.__paginationReset) grid.__paginationReset();
    var lmBtn = grid.parentNode.querySelector('.load-more-btn');
    if (lmBtn) lmBtn.style.display = 'none';

    var cards = qa('.video-card');
    cards.sort(function(a, b) {
      if (mode === 'date') return new Date(b.getAttribute('data-published')) - new Date(a.getAttribute('data-published'));
      if (mode === 'oldest') return new Date(a.getAttribute('data-published')) - new Date(b.getAttribute('data-published'));
      if (mode === 'views') return parseInt(b.getAttribute('data-views'), 10) - parseInt(a.getAttribute('data-views'), 10);
      if (mode === 'duration') return parseInt(b.getAttribute('data-duration'), 10) - parseInt(a.getAttribute('data-duration'), 10);
      if (mode === 'shortest') return parseInt(a.getAttribute('data-duration'), 10) - parseInt(b.getAttribute('data-duration'), 10);
      if (mode === 'alpha') return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
    });
    cards.forEach(function(c) { grid.appendChild(c); });
  };

  window.sortPlaylists = function(btn, mode) {
    qa('.sort-btn').forEach(function(b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');
    var container = document.getElementById('playlist-rows');
    if (!container) return;
    var rows = qa('.playlist-row');
    rows.sort(function(a, b) {
      if (mode === 'date' || mode === 'last-updated') {
        var attr = mode === 'date' ? 'data-published' : 'data-last-updated';
        return (b.getAttribute(attr) || '').localeCompare(a.getAttribute(attr) || '');
      }
      return (parseInt(b.getAttribute('data-' + mode), 10) || 0) - (parseInt(a.getAttribute('data-' + mode), 10) || 0);
    });
    rows.forEach(function(r) { container.appendChild(r); });
  };

  /* Event delegation for modal actions (chapters, up-next, series-more) */
  document.addEventListener('click', function(e) {
    var chip = e.target.closest ? e.target.closest('.chapter-chip, .chap-inline') : null;
    if (chip && _openEl) {
      var time = chip.getAttribute('data-start') || chip.getAttribute('data-chap-time');
      setIframe(_openEl.getAttribute('data-video-id'), time);
      return;
    }
    var next = e.target.closest ? e.target.closest('[data-watch-next]') : null;
    if (next && _openEl) {
      var nid = next.getAttribute('data-watch-next');
      closePlayer();
      setTimeout(function() {
        var c = q('[data-video-id="' + nid + '"]');
        if (c) openPlayer(c);
      }, 100);
      return;
    }
    var more = e.target.closest ? e.target.closest('.series-more-item') : null;
    if (more) {
      var mid = more.getAttribute('data-video-id');
      var mc = q('[data-video-id="' + mid + '"]');
      if (mc) openPlayer(mc);
      return;
    }
  });

  var MODAL_FOCUSABLE = 'a[href], button:not([disabled]), iframe[src], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  function trapFocus(e) {
    var modal = document.getElementById('video-modal');
    if (!modal || !modal.classList.contains('open')) return;

    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
      openSibling(1);
      return;
    }
    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
      openSibling(-1);
      return;
    }
    if (e.key !== 'Tab') return;

    var focusable = Array.prototype.slice.call(modal.querySelectorAll(MODAL_FOCUSABLE)).filter(function(el) {
      return el.offsetParent !== null && !el.disabled && el.getAttribute('aria-hidden') !== 'true';
    });
    if (!focusable.length) return;
    var first = focusable[0];
    var last = focusable[focusable.length - 1];
    if (e.shiftKey && (document.activeElement === first || document.activeElement === modal)) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function openSibling(dir) {
    var cards = qa('[data-video-id]');
    if (!_openEl || cards.length < 2) return;
    var idx = cards.indexOf(_openEl);
    if (idx === -1) return;
    var next = cards[(idx + dir + cards.length) % cards.length];
    openPlayer(next);
  }

  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    trapFocus(e);
  });

  /* Chapter / series-more are handled via delegation above */

  /* --- Page-level helpers --- */

  function initScheduleTimes() {
    qa('.schedule-utc').forEach(function(el) {
      var utc = el.getAttribute('datetime');
      if (!utc) return;
      var d = new Date(utc);
      var utcH = d.getUTCHours().toString().padStart(2, '0');
      var utcM = d.getUTCMinutes().toString().padStart(2, '0');
      var locH = d.getHours().toString().padStart(2, '0');
      var locM = d.getMinutes().toString().padStart(2, '0');
      var locTz = '';
      var parts = Intl.DateTimeFormat('en', { timeZoneName: 'short' }).formatToParts(d);
      for (var j = 0; j < parts.length; j++) {
        if (parts[j].type === 'timeZoneName') { locTz = ' ' + parts[j].value; break; }
      }
      el.textContent = utcH + ':' + utcM + ' UTC (' + locH + ':' + locM + locTz + ')';
    });
  }

  function initCountdown() {
    var el = document.getElementById('stream-countdown');
    if (!el) return;
    var target = el.getAttribute('data-countdown');
    if (!target) return;
    var start = new Date(target).getTime();
    function tick() {
      var diff = start - Date.now();
      if (diff <= 0) { el.textContent = 'starting soon!'; return; }
      var out = [];
      var d = Math.floor(diff / 86400000);
      var h = Math.floor((diff % 86400000) / 3600000);
      var m = Math.floor((diff % 3600000) / 60000);
      var s = Math.floor((diff % 60000) / 1000);
      if (d > 0) out.push(d + 'd');
      if (h > 0 || d > 0) out.push(h + 'h');
      out.push(m + 'm', s + 's');
      el.textContent = out.join(' ');
    }
    tick();
    setInterval(tick, 1000);
  }

  function initMarquee() {
    var track = document.getElementById('milestone-track');
    if (!track) return;
    var halfWidth = 0;
    var items = track.children;
    var half = Math.floor(items.length / 2);
    for (var i = 0; i < half; i++) halfWidth += items[i].offsetWidth;
    if (halfWidth > 0) {
      var duration = Math.max(15, halfWidth / 50);
      track.style.animationDuration = duration + 's';
    }
  }

  function initHashDeepLink() {
    var hash = window.location.hash;
    if (!hash || hash.length < 2) return;

    var name = decodeURIComponent(hash.slice(1)).replace(/\+/g, ' ');
    var isSeriesHash = false;

    qa('.filter-btn').forEach(function(btn) {
      if (!isSeriesHash && (btn.getAttribute('data-series-name') === name || btn.textContent.trim() === name)) {
        filterSeries(btn);
        btn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        isSeriesHash = true;
      }
    });
    if (isSeriesHash) return;

    var card = q('[data-video-id="' + name + '"]');
    if (!card && name.indexOf('vid-') === 0) {
      card = q('[data-video-id="' + name.slice(4) + '"]');
    }
    if (card) {
      openPlayer(card);
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  /* ---- Infinite-scroll pagination ---- */
  window.initPagination = function(gridId, batchSize) {
    var grid = document.getElementById(gridId);
    if (!grid) return;

    if (!batchSize) {
      batchSize = parseInt(grid.getAttribute('data-paged'), 10) || 30;
    }

    var cards = Array.prototype.slice.call(grid.children).filter(function(el) {
      return el.classList.contains('video-card');
    });
    if (cards.length <= batchSize) return;

    var loadMoreBtn = document.createElement('button');
    loadMoreBtn.className = 'load-more-btn';
    loadMoreBtn.textContent = 'Show more';
    grid.parentNode.insertBefore(loadMoreBtn, grid.nextSibling);

    var pageSize = batchSize;
    var currentIndex = pageSize;

    function hideAllBeyond(idx) {
      for (var i = idx; i < cards.length; i++) {
        cards[i].classList.add('paged-hidden');
        cards[i].style.display = 'none';
      }
    }

    function showBatch() {
      var end = Math.min(currentIndex + pageSize, cards.length);
      for (var i = currentIndex; i < end; i++) {
        cards[i].classList.remove('paged-hidden');
        cards[i].style.display = '';
      }
      currentIndex = end;
      if (currentIndex >= cards.length) {
        loadMoreBtn.style.display = 'none';
      } else {
        window.setTimeout(function() {
          window.scrollBy(0, 80);
        }, 50);
      }
    }

    function resetPagination() {
      for (var i = 0; i < cards.length; i++) {
        cards[i].classList.remove('paged-hidden');
        cards[i].style.display = '';
      }
      currentIndex = cards.length;
      if (loadMoreBtn) loadMoreBtn.style.display = 'none';
    }

    hideAllBeyond(pageSize);

    loadMoreBtn.addEventListener('click', showBatch);

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting && loadMoreBtn.style.display !== 'none') {
          loadMoreBtn.click();
        }
      });
    }, { rootMargin: '200px' });
    observer.observe(loadMoreBtn);

    // Expose reset so sort/filter can call it
    grid.__paginationReset = resetPagination;
  };

  document.addEventListener('DOMContentLoaded', function() {
    initScheduleTimes();
    initCountdown();
    initMarquee();
    initHashDeepLink();

    // LQIP: fade thumbnails in on load
    Array.prototype.forEach.call(document.querySelectorAll('.video-card img'), function(img) {
      if (img.complete && img.naturalWidth > 0) {
        img.classList.add('loaded');
      } else {
        img.addEventListener('load', function() { img.classList.add('loaded'); });
        img.addEventListener('error', function() { img.classList.add('loaded'); });
      }
    });

    // Paginate any grid with [data-paged]
    var pagedGrids = document.querySelectorAll('[data-paged]');
    Array.prototype.forEach.call(pagedGrids, function(g) {
      initPagination(g.id);
    });
  });
})();