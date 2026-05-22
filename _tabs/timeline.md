---
layout: page
icon: "fa-solid fa-timeline"
title: Timeline
order: 6
permalink: /timeline/
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
<div class="timeline">
  {% for h in history %}
    {% assign prev_index = forloop.index0 | minus: 1 %}
    {% if prev_index >= 0 %}
      {% assign prev = history[prev_index] %}
      {% assign crossed = nil %}

      {% assign yt_subs = h.youtube_main.subs | default: 0 %}
      {% assign prev_yt_subs = prev.youtube_main.subs | default: 0 %}
      {% assign twitch_followers = h.twitch.followers | default: 0 %}
      {% assign prev_twitch_followers = prev.twitch.followers | default: 0 %}
      {% assign yt_views = h.youtube_main.views | default: 0 %}
      {% assign prev_yt_views = prev.youtube_main.views | default: 0 %}
      {% assign yt_videos = h.youtube_main.videos | default: 0 %}
      {% assign prev_yt_videos = prev.youtube_main.videos | default: 0 %}
      {% assign orders = h.fourthwall.orders | default: 0 %}
      {% assign prev_orders = prev.fourthwall.orders | default: 0 %}

      {% assign yt_vods_subs = h.youtube_vods.subs | default: 0 %}
      {% assign prev_yt_vods_subs = prev.youtube_vods.subs | default: 0 %}
      {% assign yt_vods_videos = h.youtube_vods.videos | default: 0 %}
      {% assign prev_yt_vods_videos = prev.youtube_vods.videos | default: 0 %}
      {% assign tw_views = h.twitch.views | default: 0 %}
      {% assign prev_tw_views = prev.twitch.views | default: 0 %}

      {% assign total_audience = yt_subs | plus: yt_vods_subs | plus: twitch_followers %}
      {% assign prev_total_audience = prev_yt_subs | plus: prev_yt_vods_subs | plus: prev_twitch_followers %}
      {% assign total_views = yt_views | plus: tw_views %}
      {% assign prev_total_views = prev_yt_views | plus: prev_tw_views %}
      {% assign total_content = yt_videos | plus: yt_vods_videos %}
      {% assign prev_total_content = prev_yt_videos | plus: prev_yt_vods_videos %}

      {% if total_audience >= 100 and prev_total_audience < 100 %}{% assign crossed = "Reached 100 total followers!" %}
      {% elsif total_audience >= 500 and prev_total_audience < 500 %}{% assign crossed = "Reached 500 total followers!" %}
      {% elsif total_audience >= 1000 and prev_total_audience < 1000 %}{% assign crossed = "Reached 1,000 total followers!" %}
      {% elsif total_views >= 10000 and prev_total_views < 10000 %}{% assign crossed = "Reached 10,000 total views!" %}
      {% elsif total_views >= 50000 and prev_total_views < 50000 %}{% assign crossed = "Reached 50,000 total views!" %}
      {% elsif total_content >= 10 and prev_total_content < 10 %}{% assign crossed = "Uploaded 10 videos!" %}
      {% elsif total_content >= 25 and prev_total_content < 25 %}{% assign crossed = "Uploaded 25 videos!" %}
      {% elsif total_content >= 50 and prev_total_content < 50 %}{% assign crossed = "Uploaded 50 videos!" %}
      {% elsif total_content >= 100 and prev_total_content < 100 %}{% assign crossed = "Uploaded 100 videos!" %}
      {% elsif orders >= 1 and prev_orders < 1 %}{% assign crossed = "First store order!" %}
      {% elsif orders >= 10 and prev_orders < 10 %}{% assign crossed = "10 store orders!" %}
      {% endif %}

      {% if crossed %}
      <div class="timeline-item milestone">
        <span class="tl-date">{{ h.date }}</span>
        <span class="tl-icon">&#11088;</span>
        <span class="tl-text">{{ crossed }}</span>
      </div>
      {% else %}
      <div class="timeline-item">
        <span class="tl-date">{{ h.date }}</span>
        <span class="tl-dot"></span>
        <span class="tl-text">{{ yt_subs }} subs &middot; {{ yt_views }} views &middot; {{ yt_videos }} videos</span>
      </div>
      {% endif %}
    {% else %}
      <div class="timeline-item">
        <span class="tl-date">{{ h.date }}</span>
        <span class="tl-dot"></span>
        <span class="tl-text">{{ h.youtube_main.subs | default: 0 }} subs &middot; {{ h.youtube_main.views | default: 0 }} views &middot; {{ h.youtube_main.videos | default: 0 }} videos</span>
      </div>
    {% endif %}
  {% endfor %}
</div>

{% else %}
<div class="timeline-empty">
  <p>No historical data yet. The chart and timeline will populate as the daily tracking pipeline collects data over the coming days.</p>
  <p>Milestones like subscriber and view thresholds will automatically appear when crossed.</p>
</div>
{% endif %}