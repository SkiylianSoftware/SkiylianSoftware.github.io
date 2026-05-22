---
layout: page
icon: "fa-solid fa-list"
title: Playlists
order: 4
permalink: /playlists/
---

{% assign playlists = site.data.playlists.playlists %}
{% if playlists.size > 0 %}
<div class="playlist-page-intro">
  <p>Curated collections of videos organised by game, topic, or series. Each playlist is a chapter in the story of this channel.</p>
  <p class="playlist-cta"><a href="/videos" class="btn"><i class="fa-solid fa-filter"></i> Browse all videos by series</a></p>
</div>
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
      <div class="playlist-meta">
        <span class="playlist-count">{{ playlist.item_count }} video{% if playlist.item_count > 1 %}s{% endif %}</span>
      </div>
    </div>
  </a>
{% endfor %}
</div>
{% else %}
<p>No playlists loaded yet.</p>
{% endif %}