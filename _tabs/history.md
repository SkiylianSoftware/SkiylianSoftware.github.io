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
{{ history.size | prepend: 'History entries: ' | append: ' (first: ' | append: history.first.date | append: ', last: ' | append: history.last.date | append: ')' }}

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
var histData = {{ history | jsonify }};
console.log('Chart debug: entries=' + histData.length, 'first=' + histData[0].date, 'last=' + histData[histData.length-1].date);
console.log('Sample entry:', JSON.stringify(histData[Math.floor(histData.length/2)]));

Chart.defaults.elements.line.tension = 0.3;
Chart.defaults.elements.point.radius = 0;

var dates = histData.map(function(h) { return h.date; });

function pluck(entry, platform, field) {
  return (entry[platform] && entry[platform][field]) || 0;
}

var audienceDatasets = [
  { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'subs'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'subs'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
  { label: 'Twitch', data: histData.map(function(h) { return pluck(h, 'twitch', 'followers'); }), borderColor: '#a970ff', backgroundColor: 'rgba(169,112,255,0.05)' },
];
audienceDatasets.push({
  label: 'Total',
  data: histData.map(function(h) {
    return (pluck(h, 'youtube_main', 'subs') || 0) + (pluck(h, 'youtube_vods', 'subs') || 0) + (pluck(h, 'twitch', 'followers') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var viewsDatasets = [
  { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'views'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'views'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
  { label: 'Twitch', data: histData.map(function(h) { return pluck(h, 'twitch', 'views'); }), borderColor: '#a970ff', backgroundColor: 'rgba(169,112,255,0.05)' },
];
viewsDatasets.push({
  label: 'Total',
  data: histData.map(function(h) {
    return (pluck(h, 'youtube_main', 'views') || 0) + (pluck(h, 'youtube_vods', 'views') || 0) + (pluck(h, 'twitch', 'views') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var contentDatasets = [
  { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'videos'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'videos'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
];
contentDatasets.push({
  label: 'Total',
  data: histData.map(function(h) {
    return (pluck(h, 'youtube_main', 'videos') || 0) + (pluck(h, 'youtube_vods', 'videos') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var ordersDatasets = [
  { label: 'Fourthwall', data: histData.map(function(h) { return pluck(h, 'fourthwall', 'orders'); }), borderColor: '#c084fc', backgroundColor: 'rgba(192,132,252,0.05)' },
];

var githubDatasets = [];
{% if history[0].github %}
githubDatasets = [
  { label: 'Stars', data: histData.map(function(h) { return pluck(h, 'github', 'stars'); }), borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.05)' },
  { label: 'Followers', data: histData.map(function(h) { return pluck(h, 'github', 'followers'); }), borderColor: '#888', backgroundColor: 'rgba(136,136,136,0.05)' },
  { label: 'Forks', data: histData.map(function(h) { return pluck(h, 'github', 'forks'); }), borderColor: '#c084fc', backgroundColor: 'rgba(192,132,252,0.05)' },
];
{% endif %}

var allMetrics = {
  audience: audienceDatasets,
  views: viewsDatasets,
  content: contentDatasets,
  orders: ordersDatasets,
  github: githubDatasets,
};

console.log('Audience dataset length:', audienceDatasets[0].data.length, 'sample:', audienceDatasets[0].data.slice(0,5));
console.log('Dates length:', dates.length, 'sample:', dates.slice(0,5));
console.log('Non-zero subs count:', audienceDatasets[0].data.filter(function(v){return v>0;}).length);
console.log('Max subs:', Math.max.apply(null, audienceDatasets[0].data));

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
  {% assign prev_month = "" %}
  {% for item in ms_keys %}
    {% assign key = item[0] %}
    {% assign date = item[1] | truncate: 10, "" %}
    {% assign month = date | truncate: 7, "" %}
    {% if month != prev_month %}
    <div class="month-divider">{{ date | date: "%B %Y" }}</div>
    {% assign prev_month = month %}
    {% endif %}
    {% assign icon = "&#9679;" %}
    {% assign mclass = "" %}
    {% assign link = nil %}
    {% assign display = key %}

    {% if key contains "game_" %}
      {% assign icon = "&#127918;" %}{% assign mclass = "ms-game" %}{% assign link = "/games" %}
      {% assign rest = key | remove_first: "game_" %}
      {% if rest contains "_ep_" %}
        {% assign parts = rest | split: "_ep_" %}
        {% capture d %}{{ parts[1] }} episodes in {{ parts[0] }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_views_" %}
        {% assign parts = rest | split: "_views_" %}
        {% capture d %}{{ parts[1] }} views across {{ parts[0] }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_hours_" %}
        {% assign parts = rest | split: "_hours_" %}
        {% capture d %}{{ parts[1] }} hours in {{ parts[0] }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_return_" %}
        {% assign parts = rest | split: "_return_" %}
        {% capture d %}Back to {{ parts[0] }} after {{ parts[1] }} days{% endcapture %}{% assign display = d %}
      {% endif %}
    {% elsif key contains "age_" %}
      {% assign icon = "&#127800;" %}{% assign mclass = "ms-age" %}{% assign link = "/" %}
      {% assign display = key | remove: "age_" | append: " days old" %}
    {% elsif key contains "hiatus_" %}
      {% assign icon = "&#127987;" %}{% assign mclass = "ms-hiatus" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "hiatus_" %}
      {% capture d %}Returned after hiatus of {{ val }}+ days{% endcapture %}{% assign display = d %}
    {% elsif key contains "streak_" %}
      {% assign icon = "&#128293;" %}{% assign mclass = "ms-streak" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "streak_" %}
      {% capture d %}{{ val }}-week upload streak{% endcapture %}{% assign display = d %}
    {% elsif key contains "video_first_" %}
      {% assign icon = "&#127916;" %}{% assign mclass = "ms-video-first" %}{% assign link = nil %}
      {% assign val = key | remove: "video_first_" %}
      {% capture d %}First video to {{ val }} views{% endcapture %}{% assign display = d %}
    {% elsif key contains "hours_" %}
      {% assign icon = "&#9200;" %}{% assign mclass = "ms-hours" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "hours_" %}
      {% capture d %}{{ val }} total channel hours{% endcapture %}{% assign display = d %}
    {% else %}
      {% assign pparts = key | split: "_" %}
      {% assign val = pparts | last %}
      {% assign ptype = pparts[0] %}
      {% if key contains "views" %}{% assign icon = "&#128065;" %}{% assign mclass = "ms-views" %}{% assign link = "/videos" %}
      {% elsif key contains "videos" %}{% assign icon = "&#127916;" %}{% assign mclass = "ms-videos" %}{% assign link = "/videos" %}
      {% else %}{% assign icon = "&#11088;" %}{% assign mclass = "ms-subs" %}{% assign link = "/about" %}
      {% endif %}
      {% capture d %}{{ val }} {{ ptype }}{% endcapture %}{% assign display = d %}
    {% endif %}

    {% assign link_meta = milestones.links[key] %}
    {% if link_meta %}{% assign link = link_meta.url %}{% endif %}

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

{% else %}
<div class="timeline-empty">
  <p>No historical data yet. The chart and timeline will populate as the daily tracking pipeline collects data over the coming days.</p>
</div>
{% endif %}