---
layout: page
icon: "fa-solid fa-list"
title: Playlists
order: 3
permalink: /playlists/
---

<div class="playlist-grid">
  {% assign playlists = site.data.playlists.playlists %}
  {% if playlists.size > 0 %}
    {% for playlist in playlists %}
      <div class="playlist-card">
        <a href="{{ playlist.url }}" target="_blank">
          {% if playlist.thumbnail %}
            <img src="{{ playlist.thumbnail }}" alt="" loading="lazy" class="playlist-thumb">
          {% endif %}
          <div class="playlist-info">
            <h3>{{ playlist.title }}</h3>
            {% if playlist.description %}
              <p class="playlist-desc">{{ playlist.description | truncate: 120 }}</p>
            {% endif %}
            {% if playlist.item_count %}
              <span class="count">{{ playlist.item_count }} videos</span>
            {% endif %}
          </div>
        </a>
      </div>
    {% endfor %}
  {% else %}
    <p>No playlists loaded yet.</p>
  {% endif %}
</div>

<style>
.playlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}
.playlist-card {
  background: var(--card-bg, #1e1e1e);
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.15s;
}
.playlist-card:hover {
  transform: translateY(-3px);
}
.playlist-card a {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  text-decoration: none;
  color: inherit;
}
.playlist-thumb {
  width: 140px;
  height: 79px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}
.playlist-info {
  flex: 1;
  min-width: 0;
}
.playlist-info h3 {
  font-size: 0.9rem;
  margin: 0 0 0.2rem;
  line-height: 1.3;
}
.playlist-desc {
  font-size: 0.8rem;
  margin: 0 0 0.3rem;
  opacity: 0.65;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.playlist-card .count {
  font-size: 0.78rem;
  opacity: 0.7;
}
</style>