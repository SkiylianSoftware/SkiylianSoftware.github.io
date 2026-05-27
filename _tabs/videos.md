---
layout: page
icon: "fa-solid fa-video"
title: Videos
order: 2
permalink: /videos/
group: media
---

<div class="sort-bar">
  <button class="sort-btn active" data-sort="date" onclick="sortGrid(this, 'date')">Newest</button>
  <button class="sort-btn" data-sort="views" onclick="sortGrid(this, 'views')">Most viewed</button>
  <button class="sort-btn" data-sort="duration" onclick="sortGrid(this, 'duration')">Longest</button>
  <button class="sort-btn random-btn" onclick="randomVideo()" title="Random video">&#x1F3B2;</button>
</div>

{% assign all_videos = site.data.youtube_main.videos %}
{% if all_videos and all_videos.size > 0 %}
{% assign series_set = all_videos | map: "series" | compact | map: "series_name" | uniq %}
{% assign recency_map = site.data.youtube_main.series_recency %}
{% if series_set.size > 1 %}
<div class="filter-bar">
  <button class="filter-btn active" onclick="filterSeries(this, '')">All</button>
  {% for name in series_set %}
  {% if recency_map and recency_map != "" %}
    {% assign r = recency_map[name] %}
    {% assign recency = r.status | default: 'historical' %}
  {% else %}
    {% assign recency = 'historical' %}
  {% endif %}
  <button class="filter-btn recency-{{ recency }}" onclick="filterSeries(this, '{{ name | escape }}')"><span class="recency-dot"></span> {{ name }}</button>
  {% endfor %}
</div>
{% endif %}

<div id="video-grid" class="video-grid">
{% for video in all_videos %}
<div class="video-card" data-video-id="{{ video.video_id }}" data-title="{{ video.title | escape }}"
     data-published="{{ video.published }}" data-views="{{ video.view_count | default: 0 }}"
     data-duration="{{ video.duration_seconds | default: 0 }}"
     data-series="{% if video.series %}{{ video.series.series_name | escape }}{% endif %}"
     data-game="{% if video.series %}{{ video.series.game | escape }}{% endif %}"
     data-description="{{ video.description | escape }}"
     data-episode="{% if video.series %}{{ video.series.episode_number }}{% endif %}"
     onclick="openPlayer(this)">
  <div class="thumb-wrap">
    <img src="{{ video.thumbnail }}" alt="{{ video.title }}" loading="lazy" onerror="this.onerror=null;this.src='https://i.ytimg.com/vi/{{ video.video_id }}/hqdefault.jpg'">
    <div class="play-overlay"><i class="fas fa-play"></i></div>
    {% if video.duration_seconds and video.duration_seconds > 0 %}<span class="duration-badge">{{ video.duration_seconds | divided_by: 3600 }}:{{ video.duration_seconds | modulo: 3600 | divided_by: 60 | prepend: '00' | slice: -2, 2 }}:{{ video.duration_seconds | modulo: 60 | prepend: '00' | slice: -2, 2 }}</span>{% endif %}
  </div>
  <div class="card-body">
    <h3>{{ video.title }}</h3>
    <div class="meta-row">
      {% if video.published %}<span class="meta-date"><time datetime="{{ video.published }}">{{ video.published | date: "%d %b %Y" }}</time> <span class="reltime" datetime="{{ video.published }}"></span></span>{% endif %}
      {% if video.view_count and video.view_count > 0 %}<span class="views">{{ video.view_count }} views</span>{% endif %}
    </div>
    {% if video.series %}<div class="series-badge">{{ video.series.game }} &middot; Ep {{ video.series.episode_number }}</div>{% endif %}
    {% if video.description %}<p class="video-desc">{{ video.description | truncate: 120 }}</p>{% endif %}
  </div>
</div>
{% endfor %}
</div>
{% else %}
<p>No videos loaded yet. Check back soon!</p>
{% endif %}

<div id="video-modal" class="modal" onclick="if(event.target==this)closePlayer()">
  <div class="modal-content">
    <button class="modal-close" onclick="closePlayer()">&times;</button>
    <div class="modal-top">
      <div class="modal-video-col">
        <div id="player-wrap"></div>
      </div>
      <div class="modal-info-col">
        <p id="modal-title" class="modal-title"></p>
        <div id="modal-series-link" class="modal-series-link"></div>
        <div id="modal-description" class="modal-description"></div>
      </div>
    </div>
    <div class="modal-bottom">
      <div id="modal-meta" class="modal-meta"></div>
      <div id="modal-chapters" class="modal-chapters"></div>
      <div id="modal-next" class="modal-next"></div>
      <a id="modal-link" href="#" target="_blank" class="btn">Watch on YouTube</a>
    </div>
  </div>
</div>

<script>
function openPlayer(el) {
  var id = el.getAttribute('data-video-id');
  var title = el.getAttribute('data-title');
  var published = el.getAttribute('data-published');
  var views = el.getAttribute('data-views');
  var duration = parseInt(el.getAttribute('data-duration')) || 0;
  var series = el.getAttribute('data-series');
  var game = el.getAttribute('data-game');
  var episode = el.getAttribute('data-episode');
  var desc = el.getAttribute('data-description') || '';
  document.getElementById('player-wrap').innerHTML = '<iframe width="100%" height="100%" src="https://www.youtube.com/embed/' + id + '?autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-link').href = 'https://www.youtube.com/watch?v=' + id;

  var metaBox = document.getElementById('modal-meta');
  var metaParts = [];
  if (published) { metaParts.push('<span class="meta-date"><time datetime="' + published + '">' + new Date(published).toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric'}) + '</time></span>'); }
  if (views > 0) { metaParts.push('<span class="meta-views">' + Number(views).toLocaleString() + ' views</span>'); }
  if (duration > 0) { metaParts.push('<span class="meta-duration">' + formatDuration(duration) + '</span>'); }
  metaBox.innerHTML = metaParts.join(' &middot; ');
  metaBox.style.display = metaParts.length ? '' : 'none';

  var linkBox = document.getElementById('modal-series-link');
  var linkParts = [];
  if (series) {
    linkParts.push('<a href="/playlists/" class="series-badge-link">' + escapeHtml(series) + '</a>');
  }
  if (game) {
    linkParts.push('<a href="/timeline/" class="game-badge-link">' + escapeHtml(game) + '</a>');
  }
  if (episode) {
    linkParts.push('<span class="ep-badge">Episode ' + episode + '</span>');
  }
  linkBox.innerHTML = linkParts.join(' ');
  linkBox.style.display = linkParts.length ? '' : 'none';

  var descBox = document.getElementById('modal-description');
  if (desc) {
    descBox.innerHTML = '<p class="desc-label">Description</p><div class="desc-text">' + linkify(escapeHtml(desc).replace(/\n/g, '<br>')) + '</div>';
    descBox.style.display = '';
  } else {
    descBox.style.display = 'none';
  }

  var chaps = parseChapters(desc);
  var chapBox = document.getElementById('modal-chapters');
  if (chaps.length) {
    chapBox.innerHTML = '<p class="chapters-label">Chapters</p>' + chaps.map(function(c){return '<span class="chapter-chip" onclick="document.getElementById(\'player-wrap\').querySelector(\'iframe\').src=\'https://www.youtube.com/embed/' + id + '?start=' + c.time + '&autoplay=1\'">' + c.label + '</span>';}).join('');
    chapBox.style.display = '';
  } else {
    chapBox.style.display = 'none';
  }

  var next = findWatchNext(el);
  var nextBox = document.getElementById('modal-next');
  if (next) {
    var nid = next.getAttribute('data-video-id');
    var ntitle = next.getAttribute('data-title');
    nextBox.innerHTML = '<p class="next-label">Up next</p><div class="next-card" onclick="closePlayer();setTimeout(function(){var c=document.querySelector(\'[data-video-id=\\\'' + nid + '\\\']\');if(c)openPlayer(c);},100)"><span class="next-title">' + ntitle + '</span></div>';
    nextBox.style.display = '';
  } else {
    nextBox.style.display = 'none';
  }

  document.getElementById('video-modal').classList.add('open');
}
function closePlayer() {
  document.getElementById('player-wrap').innerHTML = '';
  document.getElementById('video-modal').classList.remove('open');
  document.getElementById('modal-chapters').innerHTML = '';
  document.getElementById('modal-description').innerHTML = '';
}
function formatDuration(secs) {
  var h = Math.floor(secs / 3600);
  var m = Math.floor((secs % 3600) / 60);
  var s = secs % 60;
  if (h > 0) return h + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  return m + ':' + String(s).padStart(2,'0');
}
function escapeHtml(t) {
  var d = document.createElement('div');
  d.appendChild(document.createTextNode(t));
  return d.innerHTML;
}
function linkify(t) {
  return t.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
}
function sortGrid(btn, mode) {
  document.querySelectorAll('.sort-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
  var grid = document.getElementById('video-grid');
  var cards = Array.from(grid.querySelectorAll('.video-card'));
  cards.sort(function(a, b) {
    if (mode === 'date') return new Date(b.getAttribute('data-published')) - new Date(a.getAttribute('data-published'));
    if (mode === 'views') return parseInt(b.getAttribute('data-views')) - parseInt(a.getAttribute('data-views'));
    if (mode === 'duration') return parseInt(b.getAttribute('data-duration')) - parseInt(a.getAttribute('data-duration'));
  });
  cards.forEach(function(c) { grid.appendChild(c); });
}
document.addEventListener('keydown', function(e) { if(e.key === 'Escape') closePlayer(); });
document.addEventListener('DOMContentLoaded', function() {
  var hash = window.location.hash;
  if (hash && hash.length > 1) {
    var name = decodeURIComponent(hash.slice(1)).replace(/\+/g, ' ');
    var btns = document.querySelectorAll('.filter-btn');
    for (var i = 0; i < btns.length; i++) {
      if (btns[i].textContent.trim() === name) {
        filterSeries(btns[i], name);
        btns[i].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        break;
      }
    }
  }
});
</script>
