---
layout: page
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
          <h3>{{ playlist.title }}</h3>
          {% if playlist.item_count %}
            <span class="count">{{ playlist.item_count }} videos</span>
          {% endif %}
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
  margin: 1rem 0;
}
.playlist-card {
  background: var(--card-bg, #1e1e1e);
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.15s;
  padding: 1.25rem;
}
.playlist-card:hover {
  transform: translateY(-3px);
}
.playlist-card h3 {
  font-size: 1.05rem;
  margin: 0 0 0.25rem;
  line-height: 1.3;
}
.playlist-card .count {
  font-size: 0.85rem;
  opacity: 0.7;
}
</style>