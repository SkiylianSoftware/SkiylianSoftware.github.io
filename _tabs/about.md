---
layout: page
icon: "fa-solid fa-user"
title: About
order: 1
permalink: /about/
jsonld:
  "@context": https://schema.org
  "@type": Person
  name: Skye
  alternateName: skiylia
  url: https://skiylia.dev
  sameAs:
    - https://www.youtube.com/@skiylia
    - https://www.twitch.tv/skiylia
    - https://github.com/SkiylianSoftware
    - https://ko-fi.com/skiylia
  image: https://yt3.ggpht.com/BtNidDhSb_vNcUXQALblvcBNOdYXF3iqI3Nj6m3nTaoVmunOum2B7aFXQACtuFt1f5YDFOGP5Q=s800-c-k-c0x00ffffff-no-rj
---

{% include banner.html %}

{% assign store = site.data.fourthwall %}

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
      {% assign playlist_url = nil %}
      {% for pl in site.data.playlists.playlists %}
        {% if pl.title contains name %}{% assign playlist_url = pl.url %}{% break %}{% endif %}
      {% endfor %}
      {% if playlist_url %}
        {% assign url = playlist_url %}
      {% else %}
        {% assign url = "/videos#" | append: name | url_encode %}
      {% endif %}
      {% assign dot = "historical" %}
      {% if info.status == "current" %}{% assign dot = "current" %}
      {% elsif info.status == "recent" %}{% assign dot = "recent" %}
      {% endif %}
      {% capture item %}<span class="series-dot {{ dot }}"></span> <a href="{{ url }}" class="btn series-btn"><strong>{{ name }}</strong></a>{% if ep_count > 0 %} <span class="ep-count">{{ ep_count }} episodes</span>{% endif %}{% endcapture %}
      {% if info.status == "current" %}
        {% capture current_html %}{{ current_html }}<li>{{ item }}</li>{% endcapture %}
      {% elsif info.status == "recent" %}
        {% capture recent_html %}{{ recent_html }}<li>{{ item }}</li>{% endcapture %}
      {% endif %}
    {% endfor %}
    {% comment %}Check playlists not matched to any parsed series for current/recent{% endcomment %}
    {% for pl in site.data.playlists.playlists %}
      {% assign already_shown = false %}
      {% for pair in site.data.youtube_main.series_recency %}
        {% if pl.title contains pair[0] or pair[0] contains pl.title %}{% assign already_shown = true %}{% break %}{% endif %}
      {% endfor %}
      {% unless already_shown %}
        {% if pl.last_updated %}
          {% assign lu_epoch = pl.last_updated | truncate: 10, "" | date: "%s" | plus: 0 %}
          {% if lu_epoch == 0 %}{% assign lu_epoch = pl.last_updated | plus: 0 %}{% endif %}
          {% if lu_epoch > 0 %}
            {% assign now_epoch = site.time | date: "%s" | plus: 0 %}
            {% assign lu_days = now_epoch | minus: lu_epoch | divided_by: 86400 %}
            {% assign status = "historical" %}
            {% assign rt = site.recency_thresholds %}
            {% assign cur_days = rt.current_days | default: 90 %}
            {% assign rec_days = rt.recent_days | default: 365 %}
            {% if lu_days < cur_days %}{% assign status = "current" %}
            {% elsif lu_days < rec_days %}{% assign status = "recent" %}
            {% endif %}
            {% if status != "historical" %}
              {% capture item %}<span class="series-dot {{ status }}"></span> <a href="{{ pl.url }}" class="btn series-btn"><strong>{{ pl.title }}</strong></a>{% if pl.item_count > 0 %} <span class="ep-count">{{ pl.item_count }} episodes</span>{% endif %}{% endcapture %}
              {% if status == "current" %}
                {% capture current_html %}{{ current_html }}<li>{{ item }}</li>{% endcapture %}
              {% else %}
                {% capture recent_html %}{{ recent_html }}<li>{{ item }}</li>{% endcapture %}
              {% endif %}
            {% endif %}
          {% endif %}
        {% endif %}
      {% endunless %}
    {% endfor %}
    {% if current_html != "" or recent_html != "" %}
    <div class="series-section">
      {% if current_html != "" %}
      <div class="series-group">
        <h3 class="series-heading current-heading"><span class="series-dot current"></span> Current</h3>
        <ul class="series-list">{{ current_html }}</ul>
      </div>
      {% endif %}
      {% if recent_html != "" %}
      <div class="series-group">
        <h3 class="series-heading recent-heading"><span class="series-dot recent"></span> Recent</h3>
        <ul class="series-list">{{ recent_html }}</ul>
      </div>
      {% endif %}
    </div>
    {% endif %}
  </div>

  <div class="about-section">
    <h2>Links</h2>
    <div class="quick-links">
      <a href="https://watch.skiylia.dev" class="btn"><i class="fab fa-youtube"></i> YouTube</a>
      <a href="https://live.skiylia.dev" class="btn"><i class="fab fa-twitch"></i> Twitch</a>
      <a href="https://vods.skiylia.dev" class="btn"><i class="fab fa-youtube"></i> VODs</a>
      {% if store.products and store.products.size > 0 %}
      <a href="https://store.skiylia.dev" class="btn"><i class="fas fa-store"></i> Merch</a>
      {% endif %}
      <a href="https://code.skiylia.dev" class="btn"><i class="fab fa-github"></i> GitHub</a>
      <a href="https://support.skiylia.dev" class="btn"><i class="fas fa-heart"></i> Support</a>
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

<p class="about-intro" style="margin-top: 2rem;">
  I count in balanced ternary. Negatives are natural (just invert + and -), radix economy peaks at three, and 3<sup>n</sup> thresholds create a beautiful spread: 1, 3, 9, 27, 81, 243, 729&hellip; where each milestone feels earned. Powers of two are for software; round numbers are for growing up in Britain. Powers of three are my own little corner of the universe.</p>
  <p>The Setun - a Soviet ternary computer built in 1958 - proved the concept works in hardware too. Balanced ternary on vacuum tubes, with magnetic drum memory and a beautifully minimal instruction set. It was reliable, economical, and decades ahead of its time. An elegant design, and I love that the same numeric system powers my milestone tracking.
</p>
