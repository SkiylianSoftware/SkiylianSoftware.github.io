---
layout: page
icon: "fa-solid fa-video"
title: Videos
order: 1
permalink: /videos/
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
{% assign recency_map = site.data.youtube_main.series_recency | default: {} %}
{% if series_set.size > 1 %}
<div class="filter-bar">
  <button class="filter-btn active" onclick="filterSeries(this, '')">All</button>
  {% for name in series_set %}
  {% assign recency = recency_map[name] | default: 'historical' %}
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
     onclick="openPlayer(this)">
  <div class="thumb-wrap">
    <img src="{{ video.thumbnail }}" alt="{{ video.title }}" loading="lazy">
    <div class="play-overlay"><i class="fas fa-play"></i></div>
    {% if video.duration_seconds and video.duration_seconds > 0 %}<span class="duration-badge">{{ video.duration_seconds | divided_by: 3600 }}:{{ video.duration_seconds | modulo: 3600 | divided_by: 60 | prepend: '00' | slice: -2, 2 }}:{{ video.duration_seconds | modulo: 60 | prepend: '00' | slice: -2, 2 }}</span>{% endif %}
  </div>
  <div class="card-body">
    <h3>{{ video.title }}</h3>
    <div class="meta-row">
      {% if video.published %}<time datetime="{{ video.published }}">{{ video.published | date: "%d %b %Y" }}</time>{% endif %}
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
    <div id="player-wrap"></div>
    <p id="modal-title" class="modal-title"></p>
    <div id="modal-chapters" class="modal-chapters"></div>
    <div id="modal-next" class="modal-next"></div>
    <a id="modal-link" href="#" target="_blank" class="btn">Watch on YouTube</a>
  </div>
</div>

<script>
function openPlayer(el) {
  var id = el.getAttribute('data-video-id');
  var title = el.getAttribute('data-title');
  document.getElementById('player-wrap').innerHTML = '<iframe width="100%" height="100%" src="https://www.youtube.com/embed/' + id + '?autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-link').href = 'https://www.youtube.com/watch?v=' + id;
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
  var desc = Array.from(document.querySelectorAll('[data-video-id="' + id + '"] .video-desc')).map(function(e){return e.textContent;})[0];
  var chaps = parseChapters(desc);
  var chapBox = document.getElementById('modal-chapters');
  if (chaps.length) {
    chapBox.innerHTML = '<p class="chapters-label">Chapters</p>' + chaps.map(function(c){return '<span class="chapter-chip" onclick="document.getElementById(\'player-wrap\').querySelector(\'iframe\').src=\'https://www.youtube.com/embed/' + id + '?start=' + c.time + '&autoplay=1\'">' + c.label + '</span>';}).join('');
    chapBox.style.display = '';
  } else {
    chapBox.style.display = 'none';
  }
  document.getElementById('video-modal').classList.add('open');
}
function closePlayer() {
  document.getElementById('player-wrap').innerHTML = '';
  document.getElementById('video-modal').classList.remove('open');
  document.getElementById('modal-chapters').innerHTML = '';
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
</script>
