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
{% assign content_types = site.data.content_types %}

{% if game_data %}
{% assign games = game_data.games %}
{% assign non_game = game_data.non_game %}
{% if games.size > 0 or non_game.total.episode_count > 0 %}
  {% if games.size > 0 %}
  <div class="games-grid">
  {% for pair in games %}
  {% assign gname = pair[0] %}
  {% assign g = pair[1] %}
  {% assign link = glinks[gname] %}
  {% assign hours = g.total_duration_seconds | divided_by: 3600 %}
  {% assign rem_secs = g.total_duration_seconds | modulo: 3600 %}
  {% assign mins = rem_secs | divided_by: 60 %}
  {% assign img_url = link.icon %}
  {% if img_url == nil and link.steam %}
    {% assign steam_parts = link.steam | split: '/' %}
    {% assign steam_appid = steam_parts[4] %}
    {% assign img_url = "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/" | append: steam_appid | append: "/header.jpg" %}
  {% endif %}
  {% assign card_link = link.steam | default: link.website %}
  {% assign ac = link.color | default: g.accent_color | default: "#2dd4bf" %}
  <div class="game-card" style="--game-accent: {{ ac }}">
    {% if card_link %}<a href="{{ card_link }}" class="game-card-stretched-link" target="_blank" rel="noopener"></a>{% endif %}
    {% if img_url %}
    <div class="game-card-img" style="background-image: url('{{ img_url }}')"></div>
    {% endif %}
    <div class="game-card-content">
      <div class="game-card-header">
        <h3 class="game-name">
          {% if img_url == nil %}<i class="fas fa-gamepad game-fallback-icon"></i>{% endif %}
          {{ gname }}
          {% if g.status == "current" %}<span class="badge badge-current">Current</span>{% endif %}
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
        <span class="game-stat"><span class="game-stat-value">{{ g.episode_count }}</span> ep</span>
        <span class="game-stat"><span class="game-stat-value">{{ hours }}h {{ mins }}m</span></span>
        <span class="game-stat"><span class="game-stat-value">{{ g.total_views }}</span> views</span>
        {% if g.engagement_rate and g.engagement_rate > 0 %}
        <span class="game-stat"><span class="game-stat-value">{{ g.engagement_rate }}%</span> engagement</span>
        {% endif %}
        {% if g.series.size > 1 %}
        <span class="game-stat"><span class="game-stat-value">{{ g.series | size }}</span> series</span>
        {% endif %}
      </div>
      <div class="game-series">
        {% if g.active_years %}
        {% if g.series_bars and g.series_bars.size > 1 %}
        <div class="game-series-bars" title="Episodes per series">
          {% for sb in g.series_bars %}
          <span class="gsb-item" title="{{ sb.name }}: {{ sb.count }} episodes">
            <span class="gsb-label">{{ sb.name }}</span>
            <span class="gsb-bar-wrap"><span class="gsb-bar" style="width:{{ sb.pct }}%"></span></span>
            <span class="gsb-count">{{ sb.count }}</span>
          </span>
          {% endfor %}
        </div>
        {% endif %}
        {% endif %}
        {% for sname in g.series %}
        {% assign sd = g.series_data[sname] %}
        {% assign pl_url = nil %}
        {% for try_name in g.original_names %}
          {% assign candidate = try_name | append: ": " | append: sname %}
          {% for pl in playlists %}
          {% if pl.title contains candidate %}
          {% assign pl_url = pl.url %}
          {% break %}
          {% endif %}
          {% endfor %}
          {% if pl_url %}
          {% break %}
          {% endif %}
        {% endfor %}
        <a href="/videos#{{ sname | url_encode }}" class="btn game-series-link{% if pl_url == nil %} no-playlist{% endif %}">{{ sname }} ({{ sd.active_years }})</a>
        {% endfor %}
      </div>
    </div>
  </div>
  {% endfor %}
  </div>
  {% endif %}

  {% if non_game.total.episode_count > 0 %}
  {% assign nhours = non_game.total.total_duration_seconds | divided_by: 3600 %}
  {% assign nrem = non_game.total.total_duration_seconds | modulo: 3600 %}
  {% assign nmins = nrem | divided_by: 60 %}
  <div class="non-game-section">
    <h2>Other Content</h2>
    <p class="non-game-desc">Videos that don't belong to a specific game series -- programming, IRL, shorts, and miscellany.</p>
    <div class="games-grid">
    {% for cat_pair in non_game.categories %}
    {% assign cat_name = cat_pair[0] %}
    {% assign cat = cat_pair[1] %}
    {% assign cat_hours = cat.total_duration_seconds | divided_by: 3600 %}
    {% assign cat_rem = cat.total_duration_seconds | modulo: 3600 %}
    {% assign cat_mins = cat_rem | divided_by: 60 %}
    {% assign cat_icon = "fa-folder-open" %}
    {% for ct in content_types %}
      {% if ct.name == cat_name %}{% assign cat_icon = ct.icon %}{% break %}{% endif %}
    {% endfor %}
    <div class="game-card non-game">
      <div class="game-card-content">
        <div class="game-card-header">
          <h3 class="game-name"><i class="fas {{ cat_icon }}"></i> {{ cat_name }}</h3>
          <div class="game-links">
            <a href="/videos" class="btn game-link-btn"><i class="fas fa-video"></i> Browse</a>
          </div>
        </div>
        <div class="game-stats">
          <span class="game-stat"><span class="game-stat-value">{{ cat.episode_count }}</span> video{% if cat.episode_count > 1 %}s{% endif %}</span>
          <span class="game-stat"><span class="game-stat-value">{{ cat_hours }}h {{ cat_mins }}m</span></span>
          <span class="game-stat"><span class="game-stat-value">{{ cat.total_views }}</span> views</span>
          {% if cat.engagement_rate and cat.engagement_rate > 0 %}
          <span class="game-stat"><span class="game-stat-value">{{ cat.engagement_rate }}%</span> engagement</span>
          {% endif %}
        </div>
        {% if cat.series_data %}
        <div class="game-series">
          {% for cs_pair in cat.series_data %}
          {% assign cs_name = cs_pair[0] %}
          {% assign csd = cs_pair[1] %}
          {% assign cs_pl_url = nil %}
          {% for pl in playlists %}
            {% if pl.title contains cs_name %}{% assign cs_pl_url = pl.url %}{% break %}{% endif %}
          {% endfor %}
          <a href="/videos#{{ cs_name | url_encode }}" class="btn game-series-link{% if cs_pl_url == nil %} no-playlist{% endif %}">{{ cs_name }} ({{ csd.active_years }})</a>
          {% endfor %}
        </div>
        {% endif %}
      </div>
    </div>
    {% endfor %}
    </div>
  </div>
  {% endif %}
{% else %}
  <p class="empty-state">Game data is loading. Check back after the next data pipeline run.</p>
{% endif %}
{% endif %}
