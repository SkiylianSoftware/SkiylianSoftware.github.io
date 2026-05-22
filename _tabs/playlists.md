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
