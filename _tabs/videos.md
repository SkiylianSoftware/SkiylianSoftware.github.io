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
{% if series_set.size > 1 %}
<div class="filter-bar">
  <button class="filter-btn active" onclick="filterSeries(this, '')">All</button>
  {% for name in series_set %}
  <button class="filter-btn" onclick="filterSeries(this, '{{ name | escape }}')">{{ name }}</button>
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

<style>
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}
.video-card {
  background: rgba(13, 13, 30, 0.8);
  border: 1px solid rgba(45, 212, 191, 0.08);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.2s, transform 0.15s;
  cursor: pointer;
}
.video-card:hover { border-color: rgba(45, 212, 191, 0.3); transform: translateY(-3px); box-shadow: 0 0 20px rgba(45, 212, 191, 0.08); }
.thumb-wrap { position: relative; }
.video-card img { width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; }
.play-overlay {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.3);
  opacity: 0; transition: opacity 0.2s;
}
.video-card:hover .play-overlay { opacity: 1; }
.play-overlay i { font-size: 3rem; color: #fff; text-shadow: 0 2px 8px rgba(0,0,0,0.5); }
.duration-badge {
  position: absolute; bottom: 0.4rem; right: 0.4rem;
  background: rgba(0,0,0,0.85); color: #fff;
  font-size: 0.75rem; font-weight: 600;
  padding: 0.15rem 0.4rem; border-radius: 4px;
  border: 1px solid rgba(45, 212, 191, 0.2);
}
.card-body { padding: 0.6rem; }
.video-card h3 { font-size: 0.9rem; margin: 0 0 0.2rem; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.meta-row { display: flex; justify-content: space-between; font-size: 0.78rem; opacity: 0.7; margin-bottom: 0.2rem; }
.series-badge { font-size: 0.75rem; opacity: 0.6; margin-bottom: 0.2rem; }
.video-desc { font-size: 0.8rem; opacity: 0.6; margin: 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center; }
.modal.open { display: flex; }
.modal-content { width: 90vw; max-width: 800px; background: #111; border-radius: 12px; overflow: hidden; }
#player-wrap { width: 100%; aspect-ratio: 16/9; }
.modal-close { position: absolute; top: 1rem; right: 1.5rem; font-size: 2rem; color: #fff; background: none; border: none; cursor: pointer; z-index: 10; }
.modal-title { margin: 0.75rem 1rem; font-size: 1rem; }
.modal .btn { margin: 0 1rem 0.75rem; }
.modal-chapters, .modal-next { margin: 0 1rem 0.75rem; }
.chapters-label, .next-label { font-size: 0.8rem; font-weight: 600; margin: 0 0 0.4rem; opacity: 0.7; }
.chapter-chip { display: inline-block; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 4px; background: rgba(45,212,191,0.1); border: 1px solid rgba(45,212,191,0.2); font-size: 0.75rem; cursor: pointer; transition: background 0.15s; }
.chapter-chip:hover { background: rgba(45,212,191,0.2); }
.next-card { padding: 0.5rem; border-radius: 6px; background: rgba(45,212,191,0.08); border: 1px solid rgba(45,212,191,0.15); cursor: pointer; transition: background 0.15s; }
.next-card:hover { background: rgba(45,212,191,0.15); }
.next-title { font-size: 0.85rem; }
.sort-bar { display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; align-items: center; }
.sort-btn {
  padding: 0.35rem 0.8rem; border-radius: 6px;
  border: 1px solid rgba(45,212,191,0.2); background: transparent;
  color: #8888aa; font-size: 0.8rem; cursor: pointer; transition: all 0.15s;
}
.sort-btn:hover { border-color: rgba(45,212,191,0.5); color: #c8c8d4; }
.sort-btn.active { background: rgba(45,212,191,0.15); border-color: #2dd4bf; color: #2dd4bf; }
.random-btn { font-size: 1.1rem; padding: 0.3rem 0.6rem; }
.filter-bar { display: flex; gap: 0.4rem; margin-bottom: 1rem; flex-wrap: wrap; }
.filter-btn {
  padding: 0.25rem 0.6rem; border-radius: 12px;
  border: 1px solid rgba(192,132,252,0.2); background: transparent;
  color: #8888aa; font-size: 0.78rem; cursor: pointer; transition: all 0.15s;
}
.filter-btn:hover { border-color: rgba(192,132,252,0.5); color: #c8c8d4; }
.filter-btn.active { background: rgba(192,132,252,0.15); border-color: #c084fc; color: #c084fc; }
#kb-help {
  position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 99999;
  display: flex; align-items: center; justify-content: center;
}
.kb-help-content {
  background: #1a1a2e; border: 1px solid rgba(45,212,191,0.3);
  border-radius: 12px; padding: 2rem; max-width: 400px; width: 90%;
}
.kb-help-content h2 { margin: 0 0 1rem; font-size: 1.2rem; }
.kb-help-content table { width: 100%; font-size: 0.85rem; }
.kb-help-content td { padding: 0.3rem 0; }
.kb-help-content kbd {
  display: inline-block; padding: 0.15rem 0.4rem; border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.05);
  font-family: inherit; font-size: 0.8rem;
}
.kb-hint { margin-top: 1rem; font-size: 0.8rem; opacity: 0.6; }
</style>