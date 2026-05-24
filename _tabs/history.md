---
layout: page
icon: "fa-solid fa-timeline"
title: History
order: 6
permalink: /history/
group: stats
---

{% assign history = site.data.history %}
{% if history and history.size > 0 %}

<div class="chart-container">
  <canvas id="growthChart"></canvas>
</div>

<div class="chart-controls">
  <button class="chart-btn active" onclick="toggleMetric('audience')" id="btn-audience">Audience</button>
  <button class="chart-btn" onclick="toggleMetric('views')" id="btn-views">Views</button>
  <button class="chart-btn" onclick="toggleMetric('content')" id="btn-content">Content</button>
  <button class="chart-btn" onclick="toggleMetric('orders')" id="btn-orders">Orders</button>
  {% if history[0].github %}
  <button class="chart-btn" onclick="toggleMetric('github')" id="btn-github">GitHub</button>
  {% endif %}
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script>
var history = {{ history | jsonify }};
var dates = history.map(function(h) { return h.date; });

function pluck(entry, platform, field) {
  return (entry[platform] && entry[platform][field]) || 0;
}

var audienceDatasets = [
  { label: 'YouTube', data: history.map(function(h) { return pluck(h, 'youtube_main', 'subs'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: history.map(function(h) { return pluck(h, 'youtube_vods', 'subs'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
  { label: 'Twitch', data: history.map(function(h) { return pluck(h, 'twitch', 'followers'); }), borderColor: '#a970ff', backgroundColor: 'rgba(169,112,255,0.05)' },
];
audienceDatasets.push({
  label: 'Total',
  data: history.map(function(h) {
    return (pluck(h, 'youtube_main', 'subs') || 0) + (pluck(h, 'youtube_vods', 'subs') || 0) + (pluck(h, 'twitch', 'followers') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var viewsDatasets = [
  { label: 'YouTube', data: history.map(function(h) { return pluck(h, 'youtube_main', 'views'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: history.map(function(h) { return pluck(h, 'youtube_vods', 'views'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
  { label: 'Twitch', data: history.map(function(h) { return pluck(h, 'twitch', 'views'); }), borderColor: '#a970ff', backgroundColor: 'rgba(169,112,255,0.05)' },
];
viewsDatasets.push({
  label: 'Total',
  data: history.map(function(h) {
    return (pluck(h, 'youtube_main', 'views') || 0) + (pluck(h, 'youtube_vods', 'views') || 0) + (pluck(h, 'twitch', 'views') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var contentDatasets = [
  { label: 'YouTube', data: history.map(function(h) { return pluck(h, 'youtube_main', 'videos'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: history.map(function(h) { return pluck(h, 'youtube_vods', 'videos'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
];
contentDatasets.push({
  label: 'Total',
  data: history.map(function(h) {
    return (pluck(h, 'youtube_main', 'videos') || 0) + (pluck(h, 'youtube_vods', 'videos') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var ordersDatasets = [
  { label: 'Fourthwall', data: history.map(function(h) { return pluck(h, 'fourthwall', 'orders'); }), borderColor: '#c084fc', backgroundColor: 'rgba(192,132,252,0.05)' },
];

var githubDatasets = [];
{% if history[0].github %}
githubDatasets = [
  { label: 'Stars', data: history.map(function(h) { return pluck(h, 'github', 'stars'); }), borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.05)' },
  { label: 'Followers', data: history.map(function(h) { return pluck(h, 'github', 'followers'); }), borderColor: '#888', backgroundColor: 'rgba(136,136,136,0.05)' },
  { label: 'Forks', data: history.map(function(h) { return pluck(h, 'github', 'forks'); }), borderColor: '#c084fc', backgroundColor: 'rgba(192,132,252,0.05)' },
];
{% endif %}

var allMetrics = {
  audience: audienceDatasets,
  views: viewsDatasets,
  content: contentDatasets,
  orders: ordersDatasets,
  github: githubDatasets,
};

var ctx = document.getElementById('growthChart').getContext('2d');
var chart = new Chart(ctx, {
  type: 'line',
  data: { labels: dates, datasets: audienceDatasets },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        labels: { color: '#8888aa', font: { size: 12 }, usePointStyle: true, padding: 16 },
      },
      tooltip: {
        backgroundColor: 'rgba(13,13,30,0.9)',
        titleColor: '#c8c8d4',
        bodyColor: '#c8c8d4',
        borderColor: 'rgba(45,212,191,0.3)',
        borderWidth: 1,
        padding: 10,
      }
    },
    scales: {
      x: {
        ticks: { color: '#8888aa', maxTicksLimit: 12 },
        grid: { color: 'rgba(45,212,191,0.05)' }
      },
      y: {
        beginAtZero: true,
        ticks: { color: '#8888aa' },
        grid: { color: 'rgba(45,212,191,0.05)' }
      }
    }
  }
});

function toggleMetric(metric) {
  document.querySelectorAll('.chart-btn').forEach(function(b) { b.classList.remove('active'); });
  document.getElementById('btn-' + metric).classList.add('active');
  chart.data.datasets = allMetrics[metric];
  chart.update();
}
</script>

<h2 class="milestones-heading">Milestones</h2>
<p class="milestones-note">&#9881;&#65039; Powers of three (ternary) are my primary counting system. Powers of two (binary) and round numbers also tracked. <a href="/about">Why ternary?</a></p>

{% assign milestones = site.data.milestones %}
{% assign ms_keys = milestones.reached %}
{% if ms_keys %}
<div class="timeline">
  {% for item in ms_keys %}
    {% assign key = item[0] %}
    {% assign date = item[1] | truncate: 10, "" %}
    {% assign icon = "&#9679;" %}
    {% assign mclass = "" %}
    {% assign link = nil %}
    {% assign display = key %}

    {% if key contains "subs_p3" %}
      {% assign icon = "&#128293;" %}{% assign mclass = "ms-subs" %}{% assign link = "/about" %}
      {% assign p = key | remove: "subs_p3_" %}{% capture d %}3^{{ p }} subscribers{% endcapture %}{% assign display = d %}
    {% elsif key contains "subs_p2" %}
      {% assign icon = "&#128187;" %}{% assign mclass = "ms-subs" %}{% assign link = "/about" %}
      {% assign p = key | remove: "subs_p2_" %}{% capture d %}2^{{ p }} subscribers{% endcapture %}{% assign display = d %}
    {% elsif key contains "subs_rnd" %}
      {% assign icon = "&#11088;" %}{% assign mclass = "ms-subs" %}{% assign link = "/about" %}
      {% assign display = key | remove: "subs_rnd_" | append: " subscribers" %}
    {% elsif key contains "views_p3" or key contains "views_p3k" %}
      {% assign icon = "&#128065;" %}{% assign mclass = "ms-views" %}{% assign link = "/videos" %}
      {% capture d %}3^{{ key | remove: "views_p3_" | remove: "views_p3k_" }} views{% endcapture %}{% assign display = d %}
    {% elsif key contains "views_p2" %}
      {% assign icon = "&#128065;" %}{% assign mclass = "ms-views" %}{% assign link = "/videos" %}
      {% capture d %}2^{{ key | remove: "views_p2_" }} views{% endcapture %}{% assign display = d %}
    {% elsif key contains "views_rnd" %}
      {% assign icon = "&#128200;" %}{% assign mclass = "ms-views" %}{% assign link = "/videos" %}
      {% assign display = key | remove: "views_rnd_" | append: " views" %}
    {% elsif key contains "videos_p3" %}
      {% assign icon = "&#127916;" %}{% assign mclass = "ms-videos" %}{% assign link = "/videos" %}
      {% capture d %}3^{{ key | remove: "videos_p3_" }} videos{% endcapture %}{% assign display = d %}
    {% elsif key contains "videos_p2" %}
      {% assign icon = "&#128421;" %}{% assign mclass = "ms-videos" %}{% assign link = "/videos" %}
      {% capture d %}2^{{ key | remove: "videos_p2_" }} videos{% endcapture %}{% assign display = d %}
    {% elsif key contains "videos_rnd" %}
      {% assign icon = "&#127910;" %}{% assign mclass = "ms-videos" %}{% assign link = "/videos" %}
      {% assign display = key | remove: "videos_rnd_" | append: " videos" %}
    {% elsif key contains "game_" %}
      {% assign icon = "&#127918;" %}{% assign mclass = "ms-game" %}{% assign link = "/games" %}
    {% elsif key contains "age_" %}
      {% assign icon = "&#127800;" %}{% assign mclass = "ms-age" %}{% assign link = "/" %}
      {% assign display = key | remove: "age_" | append: " days old" %}
    {% endif %}

    {% if link %}
    <a href="{{ link }}" class="timeline-item milestone {{ mclass }}">
      <span class="tl-date">{{ date }}</span>
      <span class="tl-icon">{{ icon }}</span>
      <span class="tl-text">{{ display }}</span>
    </a>
    {% else %}
    <div class="timeline-item milestone {{ mclass }}">
      <span class="tl-date">{{ date }}</span>
      <span class="tl-icon">{{ icon }}</span>
      <span class="tl-text">{{ display }}</span>
    </div>
    {% endif %}
  {% endfor %}
</div>
{% else %}
<div class="timeline-empty">
  <p>No milestone data yet. They'll appear here as thresholds are crossed during the data pipeline runs.</p>
</div>
{% endif %}