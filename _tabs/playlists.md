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
{% for pl in playlists %}
  <a href="{{ pl.url }}" target="_blank" class="playlist-row btn">
    {% if pl.thumbnail %}
      <img src="{{ pl.thumbnail }}" alt="" loading="lazy" class="playlist-row-thumb">
    {% endif %}
    <div class="playlist-row-info">
      <h3>{{ pl.title }}</h3>
      {% if pl.description %}
        <p class="playlist-row-desc">{{ pl.description }}</p>
      {% endif %}
      <div class="playlist-row-meta">
        <span class="playlist-row-count">{{ pl.item_count }} video{% if pl.item_count > 1 %}s{% endif %}</span>
        {% if pl.total_duration_seconds and pl.total_duration_seconds > 0 %}
          {% assign hours = pl.total_duration_seconds | divided_by: 3600 %}
          {% assign rem = pl.total_duration_seconds | modulo: 3600 %}
          {% assign mins = rem | divided_by: 60 %}
          <span class="playlist-row-duration">{{ hours }}h {{ mins }}m</span>
        {% endif %}
        {% if pl.total_views and pl.total_views > 0 %}
          <span class="playlist-row-views">{{ pl.total_views }} views</span>
        {% endif %}
        {% if pl.published %}
          <span class="playlist-row-date">{{ pl.published | date: "%b %Y" }}</span>
        {% endif %}
      </div>
    </div>
  </a>
{% endfor %}
</div>
{% else %}
<p>No playlists loaded yet.</p>
{% endif %}