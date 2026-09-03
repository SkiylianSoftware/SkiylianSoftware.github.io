---
layout: page
icon: "fa-solid fa-compass"
title: Start Here
order: 12
permalink: /start-here/
---

{% assign videos = site.data.youtube_main.videos %}
{% if videos.size == 0 %}<p>Video data is loading. Check back after the next pipeline run.</p>{% endif %}

{% if videos.size > 0 %}
{% assign games_data = site.data.games.games %}
{% for pair in games_data %}
{% assign gname = pair[0] %}
{% assign g = pair[1] %}

## {{ gname }}

{% assign game_vids = "" | split: "," %}
{% for v in videos %}{% if v.series.game == gname %}{% assign game_vids = game_vids | push: v %}{% endif %}{% endfor %}
{% assign top3 = game_vids | sort: "view_count" | reverse | slice: 0, 3 %}

<div class="video-grid">
{% for v in top3 %}
<div class="video-card" data-video-id="{{ v.video_id }}" onclick="openPlayer(this)" data-title="{{ v.title | escape }}">
  <div class="thumb-wrap">
    <img src="{{ v.thumbnail }}" alt="{{ v.title }}" loading="lazy">
    <div class="play-overlay"><i class="fas fa-play"></i></div>
  </div>
  <div class="card-body">
    <h3>{{ v.title }}</h3>
    <div class="meta-row">
      <span class="meta-date">{{ v.published | date: "%b %Y" }}</span>
      <span class="views">{{ v.view_count }} views</span>
    </div>
  </div>
</div>
{% endfor %}
</div>
{% endfor %}

## Wildcard Pick

{% assign best_eng = videos | sort: "engagement_rate" | reverse | first %}
{% if best_eng %}
<p>Highest-engagement video across all series:</p>
<div class="video-grid">
<div class="video-card" data-video-id="{{ best_eng.video_id }}" onclick="openPlayer(this)" data-title="{{ best_eng.title | escape }}">
  <div class="thumb-wrap">
    <img src="{{ best_eng.thumbnail }}" alt="{{ best_eng.title }}" loading="lazy">
    <div class="play-overlay"><i class="fas fa-play"></i></div>
  </div>
  <div class="card-body">
    <h3>{{ best_eng.title }}</h3>
    <div class="meta-row">
      <span class="meta-date">{{ best_eng.published | date: "%b %Y" }}</span>
      <span class="views">{{ best_eng.view_count }} views</span>
    </div>
  </div>
</div>
</div>
{% endif %}
{% endif %}
