---
layout: page
icon: "fa-solid fa-list"
title: Playlists
order: 4
permalink: /playlists/
group: media
---

<p class="page-intro">Complete series, collected into easy-to-binge playlists. Each one links to its archive page where you can browse every episode and subscribe to that series' feed.</p>

<div class="sort-bar">
  <button class="sort-btn active" data-sort="date" onclick="sortPlaylists(this, 'date')">Newest</button>
  <button class="sort-btn" data-sort="views" onclick="sortPlaylists(this, 'views')">Most viewed</button>
  <button class="sort-btn" data-sort="duration" onclick="sortPlaylists(this, 'duration')">Longest</button>
  <button class="sort-btn" data-sort="last-updated" onclick="sortPlaylists(this, 'last-updated')">Last video</button>
</div>

{% assign playlists = site.data.playlists.playlists %}
{% if playlists.size > 0 %}
<div class="playlist-rows" id="playlist-rows">
{% for pl in playlists %}
  {% assign recency = "historical" %}
  {% assign sr = site.data.youtube_main.series_recency %}
  {% if sr %}
    {% for pair in sr %}
      {% assign sname = pair[0] %}
      {% assign sinfo = pair[1] %}
      {% if pl.title contains sname or sname contains pl.title %}
        {% assign recency = sinfo.status | default: "historical" %}
        {% break %}
      {% endif %}
    {% endfor %}
  {% endif %}
  {% if recency == "historical" %}
    {% if pl.last_updated %}
      {% assign lu_epoch = pl.last_updated | truncate: 10, "" | date: "%s" | plus: 0 %}
      {% if lu_epoch == 0 %}{% assign lu_epoch = pl.last_updated | plus: 0 %}{% endif %}
      {% if lu_epoch > 0 %}
        {% assign now_epoch = site.time | date: "%s" | plus: 0 %}
        {% assign lu_days = now_epoch | minus: lu_epoch | divided_by: 86400 %}
        {% assign rt = site.recency_thresholds %}
        {% assign cur_days = rt.current_days | default: 90 %}
        {% assign rec_days = rt.recent_days | default: 365 %}
        {% if lu_days < cur_days %}{% assign recency = "current" %}
        {% elsif lu_days < rec_days %}{% assign recency = "recent" %}
        {% endif %}
      {% endif %}
    {% endif %}
    {% if recency == "historical" %}{% assign recency = nil %}{% endif %}
  {% endif %}
  <a id="pl-{{ pl.playlist_id }}" href="{{ pl.url }}" target="_blank" class="playlist-row btn{% if recency %} recency-{{ recency }}{% endif %}"
     data-published="{{ pl.published | default: '' }}"
     data-views="{{ pl.total_views | default: 0 }}"
     data-duration="{{ pl.total_duration_seconds | default: 0 }}"
     data-last-updated="{{ pl.last_updated | default: '' }}">
    {% if pl.thumbnail %}
      <div class="playlist-row-thumb" style="background-image: url('{{ pl.thumbnail }}')"></div>
    {% endif %}
    <div class="playlist-row-info">
      <h3>{{ pl.title }}</h3>
      {% if pl.description_parts %}
        <p class="playlist-row-desc">{{ pl.description_parts | join: "<br>" }}</p>
      {% elsif pl.description %}
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
          <span class="meta-date"><span class="playlist-row-date">{{ pl.published | date: "%b %Y" }}</span>
          <span class="reltime" datetime="{{ pl.published }}"></span></span>
        {% endif %}
        {% if pl.last_updated and pl.last_updated != pl.published %}
          <span class="meta-date"><span class="playlist-row-date">&#9655; {{ pl.last_updated | date: "%b %Y" }}</span>
          <span class="reltime" datetime="{{ pl.last_updated }}"></span></span>
        {% endif %}
        {% assign pl_series = pl.title | split: " | " | first | strip %}
        {% assign pl_game = pl.title | split: " | " | last | strip %}
        {% if pl_game == pl_series %}{% assign pl_game = "" %}{% endif %}
        <span class="playlist-row-badges">
          <a href="/series/{{ pl_series | slugify }}/" class="playlist-badge"><i class="fas fa-list-ul"></i> {{ pl_series }}</a>
          {% if pl_game and pl_game != "" %}
          <a href="/games/{{ pl_game | slugify }}/" class="playlist-badge playlist-badge-game"><i class="fas fa-gamepad"></i> {{ pl_game }}</a>
          {% endif %}
        </span>
      </div>
    </div>
  </a>
{% endfor %}
</div>
{% else %}
<p>No playlists loaded yet.</p>
{% endif %}

<script src="{{ '/assets/js/player.js' | relative_url }}" defer></script>