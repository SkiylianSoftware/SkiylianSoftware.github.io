---
layout: page
icon: "fa-solid fa-video"
title: Videos
order: 2
permalink: /videos/
group: media
---

<div class="sort-bar">
  <button class="sort-btn active" data-sort="date" onclick="sortGrid(this, 'date')">Newest</button>
  <button class="sort-btn" data-sort="oldest" onclick="sortGrid(this, 'oldest')">Oldest</button>
  <button class="sort-btn" data-sort="views" onclick="sortGrid(this, 'views')">Most viewed</button>
  <button class="sort-btn" data-sort="duration" onclick="sortGrid(this, 'duration')">Longest</button>
  <button class="sort-btn" data-sort="shortest" onclick="sortGrid(this, 'shortest')">Shortest</button>
  <button class="sort-btn" data-sort="alpha" onclick="sortGrid(this, 'alpha')">A-Z</button>
  <button class="sort-btn random-btn" onclick="randomVideo()" title="Random video">&#x1F3B2;</button>
</div>

{% assign all_videos = site.data.youtube_main.videos %}
{% if all_videos and all_videos.size > 0 %}
{% assign series_set = all_videos | map: "series" | compact | map: "series_name" | uniq %}
{% assign recency_map = site.data.youtube_main.series_recency %}
{% if site.data.playlists.playlists %}
  {% assign pl_titles = site.data.playlists.playlists | map: "title" %}
  {% assign real_set = "" | split: "," %}
  {% for name in series_set %}
    {% assign found = false %}
    {% for pl_title in pl_titles %}
      {% if pl_title contains name or name contains pl_title %}
        {% assign found = true %}
        {% break %}
      {% endif %}
    {% endfor %}
    {% if found %}
      {% assign real_set = real_set | push: name %}
    {% endif %}
  {% endfor %}
  {% assign series_set = real_set %}
{% endif %}
{% if series_set.size > 1 %}
{% assign has_hidden = false %}
{% for name in series_set %}
  {% if recency_map and recency_map != "" %}
    {% assign r = recency_map[name] %}{% assign rec = r.status | default: 'historical' %}
  {% else %}
    {% assign rec = 'current' %}
  {% endif %}
  {% if rec == 'historical' %}{% assign has_hidden = true %}{% endif %}
{% endfor %}
<div class="filter-row">
<div class="filter-bar" id="filter-bar">
  <button class="filter-btn active" onclick="filterSeries(this)">All</button>
  {% for name in series_set %}
  {% if recency_map and recency_map != "" %}
    {% assign r = recency_map[name] %}{% assign rec = r.status | default: 'historical' %}
  {% else %}
    {% assign rec = 'current' %}
  {% endif %}
  {% if rec != 'historical' %}
  <button class="filter-btn recency-{{ rec }}" data-series-name="{{ name | escape }}" onclick="filterSeries(this)"><span class="recency-dot"></span> {{ name }}</button>
  {% endif %}
  {% endfor %}
</div>
{% if has_hidden %}
<div class="filter-more-wrap">
  <button class="filter-btn filter-more-btn" id="filter-more-btn" onclick="toggleMoreFilters()">More &#9660;</button>
  <div class="filter-more-dropdown" id="filter-more-dropdown">
    {% for name in series_set %}
    {% if recency_map and recency_map != "" %}
      {% assign r = recency_map[name] %}{% assign rec = r.status | default: 'historical' %}
    {% else %}
      {% assign rec = 'current' %}
    {% endif %}
    {% if rec == 'historical' %}
    <button class="filter-btn dropdown-item" data-series-name="{{ name | escape }}" onclick="filterSeries(this)"><span class="recency-dot"></span> {{ name }}</button>
    {% endif %}
    {% endfor %}
  </div>
</div>
{% endif %}
</div>
{% endif %}

<div id="video-grid" class="video-grid">
{% for video in all_videos %}
<div class="video-card" data-video-id="{{ video.video_id }}" data-title="{{ video.title | escape }}"
     data-published="{{ video.published }}" data-views="{{ video.view_count | default: 0 }}"
     data-duration="{{ video.duration_seconds | default: 0 }}"
     data-series="{% if video.series %}{{ video.series.series_name | escape }}{% endif %}"
     data-series-slug="{% if video.series %}{{ video.series.series_name | slugify }}{% endif %}"
     data-game="{% if video.series %}{{ video.series.game | escape }}{% endif %}"
     data-game-slug="{% if video.series %}{{ video.series.game | slugify }}{% endif %}"
     data-description="{{ video.description | escape }}"
     data-episode="{% if video.series %}{{ video.series.episode_number }}{% endif %}"
     onclick="openPlayer(this)">
  <div class="thumb-wrap">
    <img src="{{ video.thumbnail }}" alt="{{ video.title }}" loading="lazy" onerror="this.onerror=null;this.src='https://i.ytimg.com/vi/{{ video.video_id }}/hqdefault.jpg'">
    <div class="play-overlay"><i class="fas fa-play"></i></div>
    {% if video.duration_seconds and video.duration_seconds > 0 %}<span class="duration-badge">{{ video.duration_seconds | divided_by: 3600 }}:{{ video.duration_seconds | modulo: 3600 | divided_by: 60 | prepend: '00' | slice: -2, 2 }}:{{ video.duration_seconds | modulo: 60 | prepend: '00' | slice: -2, 2 }}</span>{% endif %}
  </div>
  <div class="card-body">
    <h3>{{ video.title }}</h3>
    <div class="meta-row">
      {% if video.published %}<span class="meta-date"><time datetime="{{ video.published }}">{{ video.published | date: "%d %b %Y" }}</time> <span class="reltime" datetime="{{ video.published }}"></span></span>{% endif %}
      {% if video.view_count and video.view_count > 0 %}<span class="views">{{ video.view_count }} views</span>{% endif %}
    </div>
    {% if video.series %}<div class="series-badge">{{ video.series.game }} &middot; Ep {{ video.series.episode_number }}</div>{% endif %}
    {% if video.description %}<p class="video-desc">{{ video.description | truncate: 120 }}</p>{% endif %}
  </div>
</div>
{% endfor %}
</div>
{% else %}
<p>No videos loaded yet. Check back soon!</p>
{% endif %}

{% include video-modal.html %}

