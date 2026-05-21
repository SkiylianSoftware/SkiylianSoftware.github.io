---
layout: page
icon: "fa-solid fa-list"
title: Playlists
order: 3
permalink: /playlists/
---

{% assign playlists = site.data.playlists.playlists %}
{% if playlists.size > 0 %}
<div class="playlist-grid">
{% for playlist in playlists %}
  <a href="{{ playlist.url }}" target="_blank" class="playlist-card">
    {% if playlist.thumbnail %}
      <img src="{{ playlist.thumbnail }}" alt="" loading="lazy" class="playlist-thumb">
    {% endif %}
    <div class="playlist-info">
      <h3>{{ playlist.title }}</h3>
      {% if playlist.description %}
        <p class="playlist-desc">{{ playlist.description | truncate: 120 }}</p>
      {% endif %}
      <span class="playlist-count">{{ playlist.item_count }} videos</span>
    </div>
  </a>
{% endfor %}
</div>
{% else %}
<p>No playlists loaded yet.</p>
{% endif %}

<style>
.playlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}
.playlist-card {
  display: block;
  background: rgba(13, 13, 30, 0.8);
  border: 1px solid rgba(45, 212, 191, 0.08);
  border-radius: 10px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s, transform 0.15s;
}
.playlist-card:hover { border-color: rgba(45, 212, 191, 0.3); transform: translateY(-3px); box-shadow: 0 0 20px rgba(45, 212, 191, 0.08); }
.playlist-thumb { width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; }
.playlist-info { padding: 0.75rem; }
.playlist-info h3 { font-size: 0.9rem; margin: 0 0 0.25rem; line-height: 1.3; }
.playlist-desc { font-size: 0.8rem; margin: 0 0 0.3rem; opacity: 0.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.playlist-count { font-size: 0.78rem; opacity: 0.5; }
</style>