---
layout: page
icon: "fa-solid fa-list"
title: Playlists
order: 4
permalink: /playlists/
---

{% assign playlists = site.data.playlists.playlists %}
{% if playlists.size > 0 %}
<div class="playlist-rows">
{% for playlist in playlists %}
  <a href="{{ playlist.url }}" target="_blank" class="playlist-row">
    {% if playlist.thumbnail %}
      <img src="{{ playlist.thumbnail }}" alt="" loading="lazy" class="playlist-row-thumb">
    {% endif %}
    <div class="playlist-row-info">
      <h3>{{ playlist.title }}</h3>
      {% if playlist.description %}
        <p class="playlist-row-desc">{{ playlist.description }}</p>
      {% endif %}
      <span class="playlist-row-count">{{ playlist.item_count }} video{% if playlist.item_count > 1 %}s{% endif %}</span>
    </div>
  </a>
{% endfor %}
</div>
{% else %}
<p>No playlists loaded yet.</p>
{% endif %}