---
layout: page
icon: "fa-brands fa-twitch"
title: Streams
order: 3
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
