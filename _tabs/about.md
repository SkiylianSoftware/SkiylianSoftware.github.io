---
layout: page
icon: "fa-solid fa-user"
title: About
order: 1
permalink: /about/
---

{% if site.data.site_meta.description %}
  <p class="about-intro">{{ site.data.site_meta.description }}</p>
{% endif %}

<div class="about-grid">
  <div class="about-section">
    <h2>Content</h2>
    <p>I play games that let me build, automate, and optimise things -- transport networks, space programs, factories, code. The channel is where engineering ambition meets cosy chaos.</p>
    {% assign current_html = "" %}
    {% assign recent_html = "" %}
    {% for pair in site.data.youtube_main.series_recency %}
      {% assign name = pair[0] %}
      {% assign info = pair[1] %}
      {% assign ep_count = info.episodes | default: 0 %}
      {% if info.status == "current" %}
        {% capture url %}/videos#{{ name | url_encode }}{% endcapture %}
        {% capture item %}<span class="series-dot current"></span> <a href="{{ url }}" class="series-link"><strong>{{ name }}</strong></a>{% if ep_count > 0 %} ({{ ep_count }} episodes){% endif %}{% endcapture %}
        {% capture current_html %}{{ current_html }}<li>{{ item }}</li>{% endcapture %}
      {% elsif info.status == "recent" %}
        {% capture url %}/videos#{{ name | url_encode }}{% endcapture %}
        {% capture item %}<span class="series-dot recent"></span> <a href="{{ url }}" class="series-link"><strong>{{ name }}</strong></a>{% if ep_count > 0 %} ({{ ep_count }} episodes){% endif %}{% endcapture %}
        {% capture recent_html %}{{ recent_html }}<li>{{ item }}</li>{% endcapture %}
      {% endif %}
    {% endfor %}
    {% if current_html != "" or recent_html != "" %}
    <div class="series-section">
      {% if current_html != "" %}
      <div class="series-group">
        <h3 class="series-heading current-heading"><span class="series-dot current"></span> Currently Playing</h3>
        <ul class="series-list">{{ current_html }}</ul>
      </div>
      {% endif %}
      {% if recent_html != "" %}
      <div class="series-group">
        <h3 class="series-heading recent-heading"><span class="series-dot recent"></span> Recently Played</h3>
        <ul class="series-list">{{ recent_html }}</ul>
      </div>
      {% endif %}
    </div>
    {% endif %}
  </div>

  <div class="about-section">
    <h2>Links</h2>
    <div class="quick-links">
      <a href="https://watch.skiylia.dev" class="ql-item"><i class="fab fa-youtube"></i> YouTube</a>
      <a href="https://live.skiylia.dev" class="ql-item"><i class="fab fa-twitch"></i> Twitch</a>
      <a href="https://code.skiylia.dev" class="ql-item"><i class="fab fa-github"></i> GitHub</a>
      <a href="https://store.skiylia.dev" class="ql-item"><i class="fas fa-store"></i> Merch</a>
      <a href="https://vods.skiylia.dev" class="ql-item"><i class="fab fa-youtube"></i> VODs</a>
      <a href="https://support.skiylia.dev" class="ql-item"><i class="fas fa-heart"></i> Support</a>
    </div>
  </div>
</div>

{% if site.data.pc_parts.display.size > 0 %}
<div class="about-section">
  <h2>PC Setup</h2>
  <div class="pc-parts">
    {% for part in site.data.pc_parts.display %}
    <div class="part-row">
      <span class="part-component">{{ part.component }}</span>
      <span class="part-name">{% if part.url %}<a href="{{ part.url }}" target="_blank" rel="noopener">{{ part.name }}</a>{% else %}{{ part.name }}{% endif %}</span>
    </div>
    {% endfor %}
  </div>
  <p class="parts-attribution">Auto-updated from <a href="{{ site.data.pc_parts.list_url }}" target="_blank" rel="noopener">PCPartPicker</a> &middot; Runs Ubuntu</p>
</div>
{% endif %}
