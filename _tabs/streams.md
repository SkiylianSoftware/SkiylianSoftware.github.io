---
layout: page
title: Streams
order: 2
permalink: /streams/
---

<p>Catch me live on <a href="https://live.skiylia.dev">Twitch</a>. Past streams are archived on the <a href="https://vods.skiylia.dev">YouTube VODs channel</a>.</p>

<div class="video-grid">
  {% assign vods = site.data.youtube_vods.videos %}
  {% if vods.size > 0 %}
    {% for vod in vods %}
      <div class="video-card">
        <a href="{{ vod.url }}" target="_blank">
          <div class="thumb-wrap">
            <img src="{{ vod.thumbnail }}" alt="{{ vod.title }}" loading="lazy">
            {% if vod.duration_seconds and vod.duration_seconds > 0 %}
              <span class="duration-badge">{{ vod.duration_seconds | divided_by: 3600 }}:{{ vod.duration_seconds | modulo: 3600 | divided_by: 60 | prepend: '00' | slice: -2, 2 }}:{{ vod.duration_seconds | modulo: 60 | prepend: '00' | slice: -2, 2 }}</span>
            {% endif %}
          </div>
          <h3>{{ vod.title }}</h3>
          <div class="meta-row">
            {% if vod.published %}
              <time datetime="{{ vod.published }}">{{ vod.published | date: "%d %b %Y" }}</time>
            {% endif %}
            {% if vod.view_count and vod.view_count > 0 %}
              <span class="views">{{ vod.view_count }} views</span>
            {% endif %}
          </div>
        </a>
      </div>
    {% endfor %}
  {% else %}
    <p>No stream archives loaded yet. Check back soon!</p>
  {% endif %}
</div>

<style>
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
  margin: 1rem 0;
}
.video-card {
  background: var(--card-bg, #1e1e1e);
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.15s;
}
.video-card:hover {
  transform: translateY(-3px);
}
.video-card a {
  text-decoration: none;
  color: inherit;
}
.thumb-wrap { position: relative; }
.video-card img {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
  display: block;
}
.duration-badge {
  position: absolute;
  bottom: 0.4rem;
  right: 0.4rem;
  background: rgba(0,0,0,0.8);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}
.video-card h3 {
  font-size: 0.9rem;
  margin: 0.5rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  margin: 0 0.5rem 0.5rem;
  font-size: 0.78rem;
  opacity: 0.7;
}
</style>