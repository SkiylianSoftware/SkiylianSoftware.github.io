---
layout: page
icon: "fa-brands fa-twitch"
title: Streams
order: 2
permalink: /streams/
---

<p>Catch me live on <a href="https://live.skiylia.dev">Twitch</a>. Past streams are archived on the <a href="https://vods.skiylia.dev">YouTube VODs channel</a>.</p>

<div class="video-grid">
  {% assign vods = site.data.youtube_vods.videos %}
  {% if vods.size > 0 %}
    {% for vod in vods %}
      <div class="video-card" data-video-id="{{ vod.video_id }}" data-title="{{ vod.title | escape }}" onclick="openPlayer(this)">
        <div class="thumb-wrap">
          <img src="{{ vod.thumbnail }}" alt="{{ vod.title }}" loading="lazy">
          <div class="play-overlay"><i class="fas fa-play"></i></div>
          {% if vod.duration_seconds and vod.duration_seconds > 0 %}
            <span class="duration-badge">{{ vod.duration_seconds | divided_by: 3600 }}:{{ vod.duration_seconds | modulo: 3600 | divided_by: 60 | prepend: '00' | slice: -2, 2 }}:{{ vod.duration_seconds | modulo: 60 | prepend: '00' | slice: -2, 2 }}</span>
          {% endif %}
        </div>
        <div class="card-body">
          <h3>{{ vod.title }}</h3>
          <div class="meta-row">
            {% if vod.published %}
              <time datetime="{{ vod.published }}">{{ vod.published | date: "%d %b %Y" }}</time>
            {% endif %}
            {% if vod.view_count and vod.view_count > 0 %}
              <span class="views">{{ vod.view_count }} views</span>
            {% endif %}
          </div>
          {% if vod.description %}
            <p class="video-desc">{{ vod.description | truncate: 120 }}</p>
          {% endif %}
        </div>
      </div>
    {% endfor %}
  {% else %}
    <p>No stream archives loaded yet. Check back soon!</p>
  {% endif %}
</div>

<div id="video-modal" class="modal" onclick="if(event.target==this)closePlayer()">
  <div class="modal-content">
    <button class="modal-close" onclick="closePlayer()">&times;</button>
    <div id="player-wrap"></div>
    <p id="modal-title" class="modal-title"></p>
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
  document.getElementById('video-modal').classList.add('open');
}
function closePlayer() {
  document.getElementById('player-wrap').innerHTML = '';
  document.getElementById('video-modal').classList.remove('open');
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
  background: var(--card-bg, #1e1e1e);
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.15s;
  cursor: pointer;
}
.video-card:hover { transform: translateY(-3px); }
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
  background: rgba(0,0,0,0.8); color: #fff;
  font-size: 0.75rem; font-weight: 600;
  padding: 0.15rem 0.4rem; border-radius: 4px;
}
.card-body { padding: 0.6rem; }
.video-card h3 { font-size: 0.9rem; margin: 0 0 0.2rem; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.meta-row { display: flex; justify-content: space-between; font-size: 0.78rem; opacity: 0.7; margin-bottom: 0.3rem; }
.video-desc { font-size: 0.8rem; opacity: 0.6; margin: 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center; }
.modal.open { display: flex; }
.modal-content { width: 90vw; max-width: 800px; background: #111; border-radius: 12px; overflow: hidden; }
#player-wrap { width: 100%; aspect-ratio: 16/9; }
.modal-close { position: absolute; top: 1rem; right: 1.5rem; font-size: 2rem; color: #fff; background: none; border: none; cursor: pointer; }
.modal-title { margin: 0.75rem 1rem; font-size: 1rem; }
.modal .btn { margin: 0 1rem 0.75rem; }
</style>