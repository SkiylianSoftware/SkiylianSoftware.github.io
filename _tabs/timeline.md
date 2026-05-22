---
layout: page
icon: "fa-solid fa-timeline"
title: Timeline
order: 8
permalink: /timeline/
---

{% assign history = site.data.history %}
{% if history and history.size > 0 %}

<div class="chart-container">
  <canvas id="growthChart"></canvas>
</div>

<div class="chart-controls">
  <button class="chart-btn active" onclick="toggleMetric('subs')" id="btn-subs">Subscribers</button>
  <button class="chart-btn" onclick="toggleMetric('views')" id="btn-views">Views</button>
  <button class="chart-btn" onclick="toggleMetric('videos')" id="btn-videos">Videos</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script>
var history = {{ history | jsonify }};
var dates = history.map(function(h) { return h.date; });
var subsData = history.map(function(h) { return h.subs; });
var viewsData = history.map(function(h) { return h.views; });
var videosData = history.map(function(h) { return h.videos; });

var ctx = document.getElementById('growthChart').getContext('2d');
var chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: dates,
    datasets: [{
      label: 'Subscribers',
      data: subsData,
      borderColor: '#2dd4bf',
      backgroundColor: 'rgba(45,212,191,0.05)',
      fill: true,
      tension: 0.3,
      pointRadius: 2,
      pointHoverRadius: 6,
      borderWidth: 2,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(13,13,30,0.9)',
        titleColor: '#c8c8d4',
        bodyColor: '#2dd4bf',
        borderColor: 'rgba(45,212,191,0.3)',
        borderWidth: 1,
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
  var data, label, color;
  if (metric === 'subs') { data = subsData; label = 'Subscribers'; color = '#2dd4bf'; }
  else if (metric === 'views') { data = viewsData; label = 'Views'; color = '#c084fc'; }
  else { data = videosData; label = 'Videos'; color = '#fbbf24'; }
  chart.data.datasets[0].data = data;
  chart.data.datasets[0].label = label;
  chart.data.datasets[0].borderColor = color;
  chart.data.datasets[0].backgroundColor = color.replace(')', ',0.05)').replace('rgb', 'rgba');
  chart.update();
}
</script>

<h2 class="milestones-heading">Milestones</h2>
<div class="timeline">
  {% for h in history %}
    {% assign milestone = nil %}
    {% if h.subs == 100 %}{% assign milestone = "100 subscribers!" %}
    {% elsif h.subs == 500 %}{% assign milestone = "500 subscribers!" %}
    {% elsif h.subs == 1000 %}{% assign milestone = "1,000 subscribers!" %}
    {% elsif h.views == 1000 %}{% assign milestone = "1,000 views!" %}
    {% elsif h.views == 10000 %}{% assign milestone = "10,000 views!" %}
    {% endif %}
    {% if milestone %}
      <div class="timeline-item milestone">
        <span class="tl-date">{{ h.date }}</span>
        <span class="tl-icon">&#11088;</span>
        <span class="tl-text">{{ milestone }} ({{ h.subs }} subs, {{ h.views }} views)</span>
      </div>
    {% else %}
      <div class="timeline-item">
        <span class="tl-date">{{ h.date }}</span>
        <span class="tl-dot"></span>
        <span class="tl-text">{{ h.subs }} subs &middot; {{ h.views }} views &middot; {{ h.videos }} videos</span>
      </div>
    {% endif %}
  {% endfor %}
</div>

{% else %}
  <p>No historical data yet. Data will appear once the tracking pipeline runs a few times.</p>
{% endif %}
