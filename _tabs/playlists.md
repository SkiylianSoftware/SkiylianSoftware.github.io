---
layout: page
icon: "fa-solid fa-list"
title: Playlists
order: 4
permalink: /playlists/
group: media
---

<div class="sort-bar">
  <button class="sort-btn active" data-sort="date" onclick="sortPlaylists(this, 'date')">Newest</button>
  <button class="sort-btn" data-sort="views" onclick="sortPlaylists(this, 'views')">Most viewed</button>
  <button class="sort-btn" data-sort="duration" onclick="sortPlaylists(this, 'duration')">Longest</button>
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
    {% assign recency = nil %}
  {% endif %}
  <a href="{{ pl.url }}" target="_blank" class="playlist-row btn{% if recency %} recency-{{ recency }}{% endif %}"
     data-published="{{ pl.published | default: '' }}"
     data-views="{{ pl.total_views | default: 0 }}"
     data-duration="{{ pl.total_duration_seconds | default: 0 }}">
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
      </div>
    </div>
  </a>
{% endfor %}
</div>
{% else %}
<p>No playlists loaded yet.</p>
{% endif %}

<script>
function sortPlaylists(btn, mode) {
  document.querySelectorAll('.sort-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
  var container = document.getElementById('playlist-rows');
  if (!container) return;
  var rows = Array.from(container.querySelectorAll('.playlist-row'));
  rows.sort(function(a, b) {
    if (mode === 'date') {
      var da = a.getAttribute('data-published') || '';
      var db = b.getAttribute('data-published') || '';
      return db.localeCompare(da);
    }
    var va = parseInt(a.getAttribute('data-' + mode)) || 0;
    var vb = parseInt(b.getAttribute('data-' + mode)) || 0;
    return vb - va;
  });
  rows.forEach(function(r) { container.appendChild(r); });
}
</script>