---
layout: page
title: Streams
order: 2
permalink: /streams/
---

<p>Catch me live on <a href="https://twitch.tv/skiylia">Twitch</a>. Past streams are archived on the <a href="https://www.youtube.com/@skiylia/streams">YouTube VODs channel</a>.</p>

<div class="stream-grid">
  {% assign streams = site.data.vods.archives | default: site.data.youtube_vods %}
  {% if streams.size > 0 %}
    {% for stream in streams %}
      <div class="stream-card">
        <a href="{{ stream.url }}" target="_blank">
          <img src="{{ stream.thumbnail }}" alt="{{ stream.title }}" loading="lazy">
          <h3>{{ stream.title }}</h3>
          {% if stream.published %}
            <time datetime="{{ stream.published }}">{{ stream.published | date: "%d %b %Y" }}</time>
          {% endif %}
        </a>
      </div>
    {% endfor %}
  {% else %}
    <p>No stream archives loaded yet. Check back soon!</p>
  {% endif %}
</div>

<style>
.stream-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
  margin: 1rem 0;
}
.stream-card {
  background: var(--card-bg, #1e1e1e);
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.15s;
}
.stream-card:hover {
  transform: translateY(-3px);
}
.stream-card img {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
}
.stream-card h3 {
  font-size: 0.95rem;
  margin: 0.5rem;
  line-height: 1.3;
}
.stream-card time {
  display: block;
  margin: 0 0.5rem 0.5rem;
  font-size: 0.8rem;
  opacity: 0.7;
}
</style>