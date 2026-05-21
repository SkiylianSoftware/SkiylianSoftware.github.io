---
layout: page
title: Videos
order: 1
permalink: /videos/
---

<div class="video-grid">
  {% assign videos = site.data.videos.videos | default: site.data.youtube_main %}
  {% if videos.size > 0 %}
    {% for video in videos %}
      <div class="video-card">
        <a href="{{ video.url }}" target="_blank">
          <img src="{{ video.thumbnail }}" alt="{{ video.title }}" loading="lazy">
          <h3>{{ video.title }}</h3>
          {% if video.published %}
            <time datetime="{{ video.published }}">{{ video.published | date: "%d %b %Y" }}</time>
          {% endif %}
        </a>
      </div>
    {% endfor %}
  {% else %}
    <p>No videos loaded yet. Check back soon!</p>
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
.video-card img {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
}
.video-card h3 {
  font-size: 0.95rem;
  margin: 0.5rem;
  line-height: 1.3;
}
.video-card time {
  display: block;
  margin: 0 0.5rem 0.5rem;
  font-size: 0.8rem;
  opacity: 0.7;
}
</style>