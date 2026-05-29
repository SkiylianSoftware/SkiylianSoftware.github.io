---
layout: page
icon: "fa-brands fa-twitch"
title: Streams
order: 3
permalink: /streams/
group: media
---

<div id="live-status" class="live-section">
  {% if site.data.livestream.platform == "twitch" %}
  <div class="live-embed">
    <div class="live-badge">LIVE</div>
    <h2>Live on Twitch</h2>
    <iframe
      src="https://player.twitch.tv/?channel=skiylia&parent={{ site.url | remove: 'https://' | remove: 'http://' | default: 'localhost' }}"
      height="480" width="100%" allowfullscreen></iframe>
    <p class="live-title">{{ site.data.livestream.title }}</p>
    <a href="https://live.skiylia.dev" class="btn btn-primary" target="_blank">Watch on Twitch</a>
  </div>
  {% elsif site.data.livestream.platform == "youtube" %}
  <div class="live-embed">
    <div class="live-badge">LIVE</div>
    <h2>Live on YouTube</h2>
    <iframe width="100%" height="480" src="https://www.youtube.com/embed/{{ site.data.livestream.video_id }}"
      frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
    <p class="live-title">{{ site.data.livestream.title }}</p>
    <a href="https://watch.skiylia.dev" class="btn btn-primary" target="_blank">Watch on YouTube</a>
  </div>
  {% else %}
  <div class="offline-panel">
    <div class="offline-icon"><i class="fas fa-circle"></i></div>
    <div class="offline-text">
      <h2>Currently Offline</h2>
      <p>Not streaming right now. Check the schedule below for upcoming streams.</p>
      <p><a href="https://live.skiylia.dev" class="btn" target="_blank">Visit Twitch Channel</a></p>
    </div>
  </div>
  {% endif %}
</div>

{% assign twitch_sched = site.data.twitch_schedule.segments %}
{% if twitch_sched and twitch_sched.size > 0 %}
<div class="section-break"></div>

<div class="widget-card">
  <h3 class="widget-title"><i class="fas fa-calendar-alt"></i> Upcoming Streams</h3>
  <div class="widget-body">
    {% for s in twitch_sched limit: 5 %}
    {% assign start = s.start_time | date: "%A" %}
    <div class="schedule-item">
      <span class="schedule-day">{{ start }}</span>
      <span class="schedule-time">{{ s.start_time | date: "%H:%M" }}</span>
      <span class="schedule-type">{{ s.category | default: s.title | truncate: 50 }}</span>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}

<div class="section-break"></div>

<h2 class="section-title">Stream Archives</h2>

{% assign yt_vods = site.data.youtube_vods.videos %}
{% assign tw_vods = site.data.twitch_vods.videos %}
{% assign vods = yt_vods | concat: tw_vods | sort: "published" | reverse %}
{% if vods.size > 0 %}
<div class="video-grid">
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
        <span class="meta-date"><time datetime="{{ vod.published }}">{{ vod.published | date: "%d %b %Y" }}</time>
          <span class="reltime" datetime="{{ vod.published }}"></span></span>
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
</div>
{% else %}
<div class="streams-empty">
  <div class="empty-icon"><i class="fas fa-video"></i></div>
  <h3>No VODs Yet</h3>
  <p>Stream archives will appear here once I go live and save the broadcast.</p>
  <div class="streams-empty-links">
    <a href="https://live.skiylia.dev" class="btn" target="_blank"><i class="fab fa-twitch"></i> Watch on Twitch</a>
    <a href="https://vods.skiylia.dev" class="btn" target="_blank"><i class="fab fa-youtube"></i> Browse VODs</a>
  </div>
</div>
{% endif %}

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
  var wrap = document.getElementById('player-wrap');
  wrap.innerHTML = '<iframe width="100%" height="100%" src="https://www.youtube.com/embed/' + id + '?autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
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
.streams-empty {
  text-align: center;
  padding: 3rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 12px;
  background: var(--card-bg);
  border: 1px solid rgba(45, 212, 191, 0.08);
}

.streams-empty .empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  opacity: 0.4;
}

.streams-empty h3 {
  font-size: 1.1rem;
  margin: 0.5rem 0;
  opacity: 0.8;
}

.streams-empty p {
  font-size: 0.9rem;
  opacity: 0.6;
  margin: 0 0 1rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.streams-empty-links {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

.streams-empty-links .btn {
  font-size: 0.85rem;
}

.live-section {
  margin: 2rem 0;
  text-align: center;
}

.live-section .live-embed {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
}

.live-badge {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  background: #ff0000;
  color: #fff;
  font-weight: 700;
  font-size: 0.8rem;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  animation: pulse 2s infinite;
  z-index: 1;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.live-title {
  margin: 0.75rem 0;
  font-weight: 500;
}

.offline-panel {
  margin: 2rem auto;
  padding: 2rem;
  border-radius: 12px;
  background: var(--clr-card-bg);
  border: 1px solid rgba(45, 212, 191, 0.08);
  text-align: center;
  max-width: 500px;
}

.offline-panel .offline-icon i {
  font-size: 2rem;
  color: #555577;
  animation: offline-pulse 3s ease-in-out infinite;
}

@keyframes offline-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

.offline-panel h2 {
  font-size: 1.1rem;
  margin: 0.5rem 0;
}

.offline-panel p {
  font-size: 0.9rem;
  opacity: 0.7;
  margin: 0;
}

.offline-panel .btn {
  font-size: 0.85rem;
}

.section-break {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(45, 212, 191, 0.2), transparent);
  margin: 1.5rem 0;
}

.section-title {
  margin: 2rem 0 0.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.4rem;
  font-size: 1.1rem;
}

.widget-card {
  flex: 1;
  min-width: 200px;
  background: var(--card-bg);
  border: 1px solid rgba(45, 212, 191, 0.1);
  border-radius: 10px;
  padding: 1rem;
}

.widget-title {
  font-size: 0.85rem;
  margin: 0 0 0.75rem;
  opacity: 0.8;
  border-bottom: 1px solid rgba(45, 212, 191, 0.1);
  padding-bottom: 0.4rem;
}

.widget-title i {
  margin-right: 0.35rem;
  color: #c084fc;
}

.widget-body {
  font-size: 0.85rem;
}

.schedule-item {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  margin-bottom: 0.4rem;
}

.schedule-day {
  font-weight: 600;
  color: #2dd4bf;
  min-width: 4em;
}

.schedule-time {
  opacity: 0.8;
}

.schedule-type {
  opacity: 0.6;
  font-size: 0.8rem;
}
</style>
