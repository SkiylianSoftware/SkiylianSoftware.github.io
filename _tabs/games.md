---
layout: page
icon: "fa-solid fa-gamepad"
title: Games
order: 5
permalink: /games/
group: media
---

{% assign game_data = site.data.games %}
{% assign glinks = site.data.game_links %}
{% assign playlists = site.data.playlists.playlists %}

{% if game_data %}
{% assign games = game_data.games %}
{% assign non_game = game_data.non_game %}
{% if games.size > 0 or non_game.episode_count > 0 %}
  {% if games.size > 0 %}
  <div class="games-grid">
  {% for pair in games %}
  {% assign gname = pair[0] %}
  {% assign g = pair[1] %}
  {% assign link = glinks[gname] %}
  {% assign hours = g.total_duration_seconds | divided_by: 3600 %}
  {% assign rem_secs = g.total_duration_seconds | modulo: 3600 %}
  {% assign mins = rem_secs | divided_by: 60 %}
  {% assign first_year = g.first_video | truncate: 4, "" %}
  {% assign latest_year = g.latest_video | truncate: 4, "" %}
  {% assign img_url = link.icon %}
  {% if img_url == nil and link.steam %}
    {% assign steam_parts = link.steam | split: '/' %}
    {% assign steam_appid = steam_parts[4] %}
    {% assign img_url = "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/" | append: steam_appid | append: "/header.jpg" %}
  {% endif %}
  <div class="game-card">
    {% if img_url %}
    <div class="game-card-img" style="background-image: url('{{ img_url }}')"></div>
    {% endif %}
    <div class="game-card-content">
      <div class="game-card-header">
        <h3 class="game-name">
          {% if img_url == nil %}<i class="fas fa-gamepad game-fallback-icon"></i>{% endif %}
          {{ gname }}
        </h3>
        <div class="game-links">
          {% if link.steam %}
          <a href="{{ link.steam }}" class="btn game-link-btn" target="_blank" rel="noopener"><i class="fab fa-steam"></i> Steam</a>
          {% endif %}
          {% if link.website %}
          <a href="{{ link.website }}" class="btn game-link-btn" target="_blank" rel="noopener"><i class="fas fa-globe"></i> Website</a>
          {% endif %}
        </div>
      </div>
      <div class="game-stats">
        <span class="game-stat"><span class="game-stat-value">{{ g.episode_count }}</span> episode{% if g.episode_count > 1 %}s{% endif %}</span>
        <span class="game-stat"><span class="game-stat-value">{{ hours }}h {{ mins }}m</span> recorded</span>
        <span class="game-stat"><span class="game-stat-value">{{ g.total_views }}</span> views</span>
        <span class="game-stat"><span class="game-stat-value">{{ first_year }}&ndash;{{ latest_year }}</span> active</span>
      </div>
      <div class="game-series">
        {% for sname in g.series %}
        {% assign pl_url = nil %}
        {% assign full_name = gname | append: ": " | append: sname %}
        {% for pl in playlists %}
          {% if pl.title contains full_name %}{% assign pl_url = pl.url %}{% break %}{% endif %}
        {% endfor %}
        {% if pl_url %}
        <a href="{{ pl_url }}" class="btn game-series-link">{{ sname }}</a>
        {% else %}
        <span class="game-series-link no-link">{{ sname }}</span>
        {% endif %}
        {% endfor %}
      </div>
    </div>
  </div>
  {% endfor %}
  </div>
  {% endif %}

  {% if non_game.episode_count > 0 %}
  {% assign nhours = non_game.total_duration_seconds | divided_by: 3600 %}
  {% assign nrem = non_game.total_duration_seconds | modulo: 3600 %}
  {% assign nmins = nrem | divided_by: 60 %}
  {% assign nfirst = non_game.first_video | truncate: 4, "" %}
  {% assign nlatest = non_game.latest_video | truncate: 4, "" %}
  <div class="non-game-section">
    <h2>Other Content</h2>
    <p class="non-game-desc">Videos that don't belong to a specific game series -- programming, IRL, shorts, and miscellany.</p>
    <div class="game-card non-game">
      <div class="game-card-content">
        <div class="game-card-header">
          <h3 class="game-name"><i class="fas fa-code"></i> Creative &amp; Miscellaneous</h3>
          <div class="game-links">
            <a href="/videos" class="btn game-link-btn"><i class="fas fa-video"></i> Browse all videos</a>
          </div>
        </div>
        <div class="game-stats">
          <span class="game-stat"><span class="game-stat-value">{{ non_game.episode_count }}</span> video{% if non_game.episode_count > 1 %}s{% endif %}</span>
          <span class="game-stat"><span class="game-stat-value">{{ nhours }}h {{ nmins }}m</span> total</span>
          <span class="game-stat"><span class="game-stat-value">{{ non_game.total_views }}</span> views</span>
          <span class="game-stat"><span class="game-stat-value">{{ nfirst }}&ndash;{{ nlatest }}</span> active</span>
        </div>
      </div>
    </div>
  </div>
  {% endif %}
{% else %}
  <p class="empty-state">Game data is loading. Check back after the next data pipeline run.</p>
{% endif %}
{% endif %}
